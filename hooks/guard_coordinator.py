#!/usr/bin/env python3
"""PreToolUse(Edit|Write|NotebookEdit|Bash) guard for the coordinator role.

The coordinator session orchestrates and never produces a deliverable itself
(RET-005: the rule only lived in the agent's memory and was broken twice). This
hook makes it enforceable. It is active only when JAM_ROLE is "coordinateur";
for any other role it exits 0 at once, without output.

Allowed writes (paths are normalised first, so a ".." cannot climb out):
  - ~/.claude/projects/*/memory/**      the coordinator's own memory
  - ~/.claude/plans/*.md                the plan mode file
  - /private/tmp/claude-*/** and /tmp/claude-*/**   session scratch space
  - /dev/null, /dev/stdout, /dev/stderr, /dev/tty   (shell targets only)

Covered:
  - Edit, Write, NotebookEdit outside the allowed paths
  - Bash: sed -i, redirections > >> >| &> &>> (2>&1, >&2 and friends ignored),
    tee, cp (destination), mv (sources AND destination, since the source
    disappears), also behind shell keywords (do, then, {, !...), xargs and
    find -exec (where "{}" is an unresolvable target)
  - bash/sh/zsh: the -c string, or the heredoc that is their script, is
    checked as shell
  - python: open() (builtin, io/os/codecs..., or path.open()) in a w/a/x/+ mode
    or a mode it cannot read, write_text(), write_bytes(), in -c code or in the
    heredoc that is its script. The code is parsed with ast; the target must be
    a literal path, possibly wrapped in Path(), .expanduser() or
    os.path.expanduser(); any computed target is refused as unresolvable. Code
    that does not parse is refused if it mentions open( or write_text/bytes.
  - Relative paths are resolved against the hook cwd, following literal `cd`.
  - A glob is accepted only in the file name of a shell target (it never
    crosses a "/"), and not after a leading "." (".*" matches ".."). Brace
    expansion is refused as unresolvable.

Exception, on purpose: installing a hook, i.e. `cp` whose sources all sit
directly in a .../hooks-staging/ folder under /private/tmp/claude-*/ or
/tmp/claude-*/, and whose destination is ~/.claude/hooks/ or a file directly in
it. Only cp: mv, redirections and Write into ~/.claude/hooks stay refused.
The hook does not check that the staged file was reviewed: anything written to
hooks-staging/ can be installed this way, this guard included.
Registering the hook in settings.json is left to the maintainer.

NOT covered (this is a tripwire against slips, not a sandbox):
  - other writing commands: rm, touch, mkdir, ln, dd, truncate, install, rsync,
    perl -i, patch, git apply/checkout/restore, npm/pip installs, editors...
  - scripts written to the scratch space then executed, other interpreters
    (node, ruby...), python writes through shutil, os.rename, subprocess...
  - eval, variables or command substitutions building a command, aliases
  - a command substitution inside double quotes: "$(cat a > src/f)" is not read
  - a `cd` inside a subshell is followed as if it applied to the rest;
    pushd/popd are not followed at all
  - heredoc detection ignores quotes: a "<< word" inside a quoted argument with
    no closing line swallows the rest of the command (rare false positive)
  - symlinks: an allowed path that links elsewhere is still allowed
  - side effects of git, gh and orca (by design, they stay open)

Exit codes:
  0 -> allow
  2 -> block, stderr is fed back to Claude as the reason
"""
import ast
import json
import os
import re
import shlex
import sys

ROLE = "coordinateur"
FILE_TOOLS = {"Edit": "file_path", "Write": "file_path", "NotebookEdit": "notebook_path"}

HOME = os.path.normpath(os.path.expanduser("~"))
# The process of the plugin running this guard, found from this file: the
# session's repo may hold no process at all, or an outdated copy.
PLUGIN_PROCESS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "process", "README.md")
HOOKS_DIR = os.path.join(HOME, ".claude", "hooks")

ALLOWED = [
    re.compile(re.escape(HOME) + r"/\.claude/projects/[^/]+/memory/.+"),
    re.compile(re.escape(HOME) + r"/\.claude/plans/[^/]+\.md"),
    re.compile(r"(?:/private)?/tmp/claude-[^/]+/.+"),
]
DEVICES = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"}
# Glob characters are tolerated in the file name of an install source.
STAGING_SOURCE = re.compile(r"(?:/private)?/tmp/claude-[^/]+/(?:.+/)?hooks-staging/[^/]+")

# Shell words that only introduce the real command.
WRAPPERS = {"sudo", "command", "exec", "env", "nohup", "time",
            "if", "then", "elif", "else", "while", "until", "do", "!", "{"}
SHELLS = {"sh", "bash", "zsh", "dash"}
XARGS_VALUE = {"-n", "-I", "-L", "-P", "-d", "-s", "-E", "-a"}
FIND_EXEC = {"-exec", "-ok", "-execdir", "-okdir"}
PUNCT = set("();<>|&")
GT = "\x00"  # stands for a quoted or escaped ">" while tokenising

HEREDOC = re.compile(r"(?<!<)<<(-?)\s*(?:'([^']*)'|\"([^\"]*)\"|\\?([A-Za-z_]\w*))")
HEREDOC_MARK = re.compile(r"HEREDOC_BODY_(\d+)")
PYTHON = re.compile(r"python[\d.]*")
# Raw hints used when the shell text cannot be tokenised at all.
WRITE_HINT = re.compile(r">|\bsed\b.*\s-[a-zA-Z]*i|\btee\b|\bcp\b|\bmv\b|\bopen\(|write_(?:text|bytes)")
PY_WRITE_HINT = re.compile(r"\bopen\s*\(|write_(?:text|bytes)")
# Modules whose open() takes (file, mode) like the builtin.
OPEN_MODULES = {"builtins", "io", "os", "codecs", "gzip", "bz2", "lzma", "tarfile"}


def fail(what):
    print(
        f"[jam] BLOQUÉ : {what}.\n"
        "Le coordinateur ne produit pas de livrable : délègue à un rôle "
        f"({PLUGIN_PROCESS}).\n"
        "Écritures permises : la mémoire (~/.claude/projects/*/memory/), "
        "le plan (~/.claude/plans/*.md), /tmp/claude-*/ et /private/tmp/claude-*/, "
        "et l'installation d'un hook relu (cp depuis .../hooks-staging/ vers "
        "~/.claude/hooks/).",
        file=sys.stderr,
    )
    sys.exit(2)


# --- paths -----------------------------------------------------------------

def resolve(path, cwd):
    """Absolute normalised path, or None when the shell would compute it."""
    path = re.sub(r"\$\{HOME\}|\$HOME\b", HOME, path)
    if path == "~" or path.startswith("~/"):
        path = HOME + path[1:]
    if re.search(r"[$`]", path) or path.startswith("~"):
        return None
    if not os.path.isabs(path):
        if cwd is None:
            return None
        path = os.path.join(cwd, path)
    return os.path.normpath(path)


def allowed(path):
    return path is not None and any(rx.fullmatch(path) for rx in ALLOWED)


def unresolvable(raw, path):
    """True when the shell may expand this target beyond what we can see."""
    # Braces are looked for in the raw text: normpath can eat "{x,.." + "..".
    if path is None or re.search(r"(?<!\$)\{", raw):
        return True
    folder, name = os.path.split(path)
    globbed = re.search(r"[*?\[]", name)
    return bool(re.search(r"[*?\[]", folder) or (globbed and name.startswith(".")))


def check_target(raw, cwd, what):
    path = resolve(raw, cwd)
    if path in DEVICES:
        return
    if unresolvable(raw, path):
        fail(f"{what} vers une cible non résolvable ({raw!r})")
    if not allowed(path):
        fail(f"{what} vers {path}")


# --- shell parsing ---------------------------------------------------------

def split_heredocs(cmd):
    """Return (shell text, heredoc bodies).

    In the shell text each heredoc becomes "<< HEREDOC_BODY_<n>", so the
    command that reads body n can be found once the text is tokenised.
    """
    shell, bodies, pending = [], [], []

    def mark(m):
        pending.append((m.group(2) or m.group(3) or m.group(4) or "", bool(m.group(1)),
                        len(bodies)))
        bodies.append([])
        return f"<< HEREDOC_BODY_{len(bodies) - 1}"

    for line in cmd.split("\n"):
        if pending:
            delimiter, strip_tabs, n = pending[0]
            if (line.lstrip("\t") if strip_tabs else line).rstrip() == delimiter:
                pending.pop(0)
            else:
                bodies[n].append(line)
            continue
        shell.append(HEREDOC.sub(mark, line))
    return "\n".join(shell), ["\n".join(body) for body in bodies]


def mask_shell(text):
    """Hide quoted/escaped ">" and comments, turn unquoted newlines into ";"."""
    out, quote, i = [], None, 0
    while i < len(text):
        c = text[i]
        if c == "\\" and quote != "'" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "\n" and not quote:
                out.append(" ")  # line continuation
            else:
                out.append(GT if nxt == ">" else c + nxt)
            i += 2
            continue
        if quote:
            if c == quote:
                quote = None
            out.append(GT if c == ">" else c)
        elif c in "'\"":
            quote = c
            out.append(c)
        elif c == "#" and (i == 0 or text[i - 1] in " \t\n;&|()"):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        else:
            out.append(" ; " if c == "\n" else c)
        i += 1
    return "".join(out)


def tokenize(shell):
    lexer = shlex.shlex(mask_shell(shell), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def simple_commands(tokens):
    """Yield (argv, redirection targets, heredoc numbers) for each simple command."""
    argv, targets, heredocs, i = [], [], [], 0
    while i < len(tokens):
        tok = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if not tok or not set(tok) <= PUNCT:
            argv.append(tok.replace(GT, ">"))
        elif ">" in tok and "(" not in tok:
            if argv and argv[-1].isdigit():
                # The fd number of "2>". shlex drops adjacency, so the 1 of
                # "echo 1 > f" goes too: harmless, no check reads it.
                argv.pop()
            if nxt is not None and not (tok.endswith(">&") and re.fullmatch(r"\d*-?", nxt)):
                targets.append(nxt.replace(GT, ">"))
            i += 1
        elif tok == "<<" and nxt and HEREDOC_MARK.fullmatch(nxt):
            heredocs.append(int(HEREDOC_MARK.fullmatch(nxt).group(1)))
            i += 1
        elif tok in ("<", "<<", "<<<", "<<-", "<&"):
            i += 1
        else:
            yield argv, targets, heredocs
            argv, targets, heredocs = [], [], []
        i += 1
    yield argv, targets, heredocs


def positionals(args, takes_value=()):
    """Split args into (positionals, {flag: value}) for the few flags we need."""
    pos, values, it = [], {}, iter(args)
    for arg in it:
        if arg == "--":
            pos.extend(it)
        elif arg in takes_value:
            values.setdefault(arg, []).append(next(it, ""))
        elif arg.startswith("--") and "=" in arg:
            flag, value = arg.split("=", 1)
            values.setdefault(flag, []).append(value)
        elif arg.startswith("-") and arg != "-":
            continue
        else:
            pos.append(arg)
    return pos, values


def stdin_is_script(args):
    """True when an interpreter reads its program from stdin (no script file)."""
    pos = positionals(args)[0]
    return not pos or pos[0] == "-"


def is_install(sources, dest, cwd):
    """cp of reviewed files from .../hooks-staging/ into ~/.claude/hooks/."""
    dest = resolve(dest, cwd)
    if dest is None or not (dest == HOOKS_DIR or os.path.dirname(dest) == HOOKS_DIR):
        return False
    resolved = [resolve(s, cwd) for s in sources]
    return bool(resolved) and all(s and STAGING_SOURCE.fullmatch(s) for s in resolved)


def strip_wrappers(argv):
    while argv and (re.match(r"[A-Za-z_]\w*=", argv[0]) or argv[0] in WRAPPERS):
        argv = argv[1:]
    return argv


def check_command(argv, cwd, heredocs=()):
    argv = strip_wrappers(argv)
    if not argv:
        return
    name, args = os.path.basename(argv[0]), argv[1:]

    if name == "xargs":
        i = 0
        while i < len(args) and args[i].startswith("-"):
            i += 2 if args[i] in XARGS_VALUE else 1
        check_command(args[i:], cwd)
    elif name == "find":
        for k, arg in enumerate(args):
            if arg in FIND_EXEC:
                sub = args[k + 1:]
                end = next((j for j, a in enumerate(sub) if a in (";", "+")), len(sub))
                # -execdir runs in each match's folder: relative targets are unknown.
                check_command(sub[:end], cwd if arg in ("-exec", "-ok") else None)
    elif name in SHELLS:
        flag = next((k for k, a in enumerate(args[:-1])
                     if re.fullmatch(r"-[a-z]*c[a-z]*", a)), None)
        if flag is not None:
            check_bash(args[flag + 1], cwd)
        elif stdin_is_script(args):
            for body in heredocs:
                check_bash(body, cwd)
    elif PYTHON.fullmatch(name):
        if "-c" in args[:-1]:
            check_python(args[args.index("-c") + 1], cwd)
        elif stdin_is_script(args):
            for body in heredocs:
                check_python(body, cwd)
    elif name == "sed":
        if not any(a.startswith("--in-place") or re.match(r"-[a-zA-Z]*i", a)
                   for a in args):
            return
        args = [a for k, a in enumerate(args)
                if not (a == "" and k and args[k - 1] == "-i")]  # BSD: -i ''
        files, values = positionals(args, ("-e", "-f", "--expression", "--file"))
        if not values:
            files = files[1:]  # the first positional is the script
        if not files:
            fail("sed -i sans fichier explicite (cible non résolvable)")
        for target in files:
            check_target(target, cwd, "sed -i")
    elif name == "tee":
        for target in positionals(args)[0]:
            check_target(target, cwd, "tee")
    elif name in ("cp", "mv"):
        pos, values = positionals(args, ("-t", "--target-directory", "-S"))
        target_dir = (values.get("-t") or values.get("--target-directory") or [None])[-1]
        if target_dir is None and len(pos) < 2:
            return
        sources, dest = (pos, target_dir) if target_dir else (pos[:-1], pos[-1])
        if name == "cp" and is_install(sources, dest, cwd):
            return
        if name == "mv":
            for source in sources:
                check_target(source, cwd, "mv (la source disparaît)")
        check_target(dest, cwd, name)


# --- python writes ---------------------------------------------------------

def dotted(node):
    """"os.path.expanduser" for that attribute chain, None for anything else."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return base and f"{base}.{node.attr}"
    return None


def literal_path(node):
    """The path a python expression names, or None if it is computed."""
    expand = False
    while isinstance(node, ast.Call) and len(node.args) <= 1 and not node.keywords:
        func = node.func
        if dotted(func) in ("Path", "pathlib.Path") and node.args:
            node = node.args[0]
        elif dotted(func) == "os.path.expanduser" and node.args:
            node, expand = node.args[0], True
        elif isinstance(func, ast.Attribute) and func.attr == "expanduser" and not node.args:
            node, expand = func.value, True
        else:
            return None
    if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
        return None
    path = node.value
    if path.startswith("~") and not expand:
        path = "./" + path  # Python does not expand "~" by itself
    return path


def is_write_mode(node):
    """A literal mode with w/a/x/+, or a mode we cannot read (os.O_WRONLY...)."""
    if node is None:
        return False
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        # Not a mode at all (webbrowser.open(url)...): not a file write.
        return bool(re.fullmatch(r"[rwaxbtU+]+", node.value)
                    and set(node.value) & set("wax+"))
    return True


def check_python(code, cwd):
    try:
        tree = ast.parse(code)
    except Exception:
        if PY_WRITE_HINT.search(code):
            fail("code python non analysable contenant une écriture possible")
        return

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))):
            continue
        func = node.func
        name = func.id if isinstance(func, ast.Name) else func.attr
        kwargs = {k.arg: k.value for k in node.keywords}
        if name in ("write_text", "write_bytes") and isinstance(func, ast.Attribute):
            check_python_target(literal_path(func.value), cwd, f"écriture python {name}()")
        elif name == "open":
            # open(file, mode) for the builtin and OPEN_MODULES, path.open(mode) otherwise.
            if isinstance(func, ast.Name) or dotted(func.value) in OPEN_MODULES:
                args = node.args
            else:
                args = [func.value] + node.args
            target = args[0] if args else kwargs.get("file")
            mode = args[1] if len(args) > 1 else kwargs.get("mode", kwargs.get("flags"))
            if is_write_mode(mode):
                check_python_target(literal_path(target), cwd, "écriture python open()")


def check_python_target(target, cwd, what):
    if target is None:
        fail(f"{what} vers une cible non résolvable (utilise un chemin littéral)")
    check_target(target, cwd, what)


# --- entry point -----------------------------------------------------------

def check_bash(cmd, cwd):
    shell, bodies = split_heredocs(cmd)
    try:
        tokens = tokenize(shell)
    except ValueError:
        if WRITE_HINT.search(shell):
            fail("commande shell non analysable contenant une écriture possible")
        return

    for argv, targets, heredocs in simple_commands(tokens):
        for target in targets:
            check_target(target, cwd, "redirection")
        program = strip_wrappers(argv)
        if program and program[0] == "cd":
            dest = program[1] if len(program) > 1 else "~"
            cwd = resolve(dest, cwd) if dest != "-" else None
            continue
        # Python and shell code is judged here, with the cwd it runs in.
        check_command(argv, cwd, [bodies[n] for n in heredocs])


def main():
    if os.environ.get("JAM_ROLE", "").strip().lower() != ROLE:
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if not isinstance(data, dict):
        sys.exit(0)

    tool = data.get("tool_name")
    if not isinstance(tool, str):
        sys.exit(0)
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    cwd = data.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = None  # unknown: relative targets are refused as unresolvable

    if tool in FILE_TOOLS:
        path = tool_input.get(FILE_TOOLS[tool])
        if isinstance(path, str) and path:
            resolved = resolve(path, cwd)
            if not allowed(resolved):
                fail(f"{tool} sur {resolved or path}")
    elif tool == "Bash":
        cmd = tool_input.get("command")
        if isinstance(cmd, str):
            check_bash(cmd, cwd)
    sys.exit(0)


if __name__ == "__main__":
    main()
