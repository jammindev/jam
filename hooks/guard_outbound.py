#!/usr/bin/env python3
"""PreToolUse(Bash) guard: the single outbound guard of the plugin.

No git commit, git push or gh write unless the maintainer's latest message in
the session transcript approves it. "gh write" means every gh command that is
not on the read list below (refused by default: a new or forgotten subcommand
is refused, not let through). git commit and push are recognised behind
global options (-C <path>, -c <key=value>, quoted or not, --no-pager,
--git-dir=…). A `!` command of the maintainer (its input and output) and the
output of a `/` command are not their words, and are skipped like tool
results. A `/` command itself is read as a message of the maintainer reduced
to its arguments: a skill opens a turn, and the approval given before it is
stale; the command name does not count. A message with a negation (ne … pas,
n'… pas, pas de, pas d', non, attends, stop, jamais) is a refusal, even with
an approval word in it; any case, across lines, with a straight, curly or
lost apostrophe (n … pas, pas d accord).

gh reads, never refused: pr list|view|status|diff|checks|checkout,
issue list|view|status, repo view|list|clone, run list|view|watch|download,
workflow list|view, release list|view|download, label list, search, status,
browse, auth status, help, version, --version; `api` with no method or
GET/HEAD and no field (-f, -F, --field, --raw-field, --input); `api graphql`
without "mutation" and with its query in sight (no --input, no -F/--field
value starting with @: a query read from a file or stdin cannot be checked).
gh is recognised behind rtk (and rtk proxy), env assignments and a few
shell keywords, by an absolute path, with -R/--repo, inside `bash -c`, and
inside a command substitution, $(…) or backticks, quoted or not.

The session scratch folders (/tmp/claude-*, /private/tmp/claude-*) exempt
commit and push only: gh writes remotely wherever it runs from.

NOT covered (a tripwire, not a sandbox):
  - gh run through eval, a variable, an alias or a script file;
  - a git alias (`git ci`, `git -c alias.ci=commit ci`);
  - gh behind a wrapper the guard does not know, or one with options before
    gh: `timeout 60 gh …`, `nice gh …`, `xargs gh …` (`echo 1 | xargs gh pr
    merge` passes, while `xargs git commit` is refused: the git regexes read
    the whole line), `find … -exec gh … ;`, `env -i gh …`, `sudo -u x gh …`;
    and a redirection before the command (`>out.txt gh pr merge 1`, where
    out.txt reads as the command name);
  - a GraphQL query hidden in a variable or a substitution
    (`-f query="$Q"`, `-f query="$(cat q.graphql)"`) passes as a read, while
    `-F query=@q.graphql`, which amounts to the same, is refused;
  - the scratch-folder exemption looks at the cwd only: from /tmp/claude-*,
    `git -C ~/repo push` or `cd ~/repo && git push` pass without approval;
  - a negation outside the maintainer's list reads as an approval: "push pas
    encore", "merge pas" (no "ne"), "ne merge plus", "ne push rien".
Refused although they only read: `gh <command> <subcommand> --help` (bare
`gh --help` and `gh pr` pass); `git --help commit`, where --help reads as a
global option; heredoc bodies are read as shell, so a body that mentions a
gh write is refused like the command itself, and so is a single-quoted
'$(gh pr merge 1)', which the shell would not run.
Refused although approved: after a local `/` command such as /model, which
opens no turn, a write waits for the maintainer's next message; a message
whose negation means no refusal ("pas de souci, go", "ok, non bloquant"), and
a relay holding one ("ce n'est pas le feu vert merge"): the maintainer
rephrases.

Exit codes:
  0 -> allow
  2 -> block, stderr is fed back to Claude as the reason. Input that is not
       the payload Claude Code sends lets through; a crash once a write is
       recognised blocks, and so does an unreadable transcript.
"""
import json
import os
import re
import shlex
import sys

# git global options that may stand between git and the verb: -C <path>,
# -c <key=value> (an agent adds `-c commit.gpgsign=false` when signing fails),
# the long options that take their value after a space, any other long option
# with or without =value, and -p/-P. A value may hold quotes anywhere
# (user.name="A B", ~/"a b") and escaped characters (/a\ b). One character
# class per turn of the loop: a [^…]+ nested in + would backtrack exponentially.
GIT_VALUE = r"""(?:"[^"]*"|'[^']*'|\\.|[^\s;|&"'\\])+"""
GIT_GLOBAL = (rf"(?:-[Cc]\s+{GIT_VALUE}"
              rf"|--(?:git-dir|work-tree|namespace|config-env|attr-source)\s+{GIT_VALUE}"
              rf"|--[\w-]+(?:={GIT_VALUE})?|-[pP])")

# git actions that leave the machine or write history. The maintainer's
# standing rule is that each of them needs an explicit go-ahead in the turn
# that triggers it.
OUTBOUND = [
    (rf"\bgit(?:\s+{GIT_GLOBAL})*\s+commit\b(?![^;|&\n]*--dry-run)", "git commit"),
    (rf"\bgit(?:\s+{GIT_GLOBAL})*\s+push\b(?![^;|&\n]*--dry-run)", "git push"),
]

# Messages that Claude Code writes for a `!` command of the maintainer, and
# for the output of a `/` command: not their words (`! git status` prints
# "nothing to commit", which reads as an approval). Neither opens a turn.
LOCAL_COMMAND = re.compile(
    r"<(?:bash-input|bash-stdout|bash-stderr|local-command-stdout|local-command-stderr)>")
# A `/` command itself (<command-message> comes first for a skill). A skill
# opens a turn of the agent, so the approval given before it is stale: the
# message is read, reduced to its arguments, the maintainer's words. The
# command name does not count (`/merge` is no approval).
SLASH_COMMAND = re.compile(r"<(?:command-name|command-message)>")
SLASH_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)

# The maintainer's approval vocabulary, mined from real transcripts.
APPROVAL = (
    r"\b("
    r"ok|oui|ouai?s?|d'accord|dac|go|vas?[-\s]?y|allez|c'est parti|"
    r"parfait|nickel|top|valide|approuve|"
    r"fai[ts][-\s]?le|fais[-\s]?la|envoie|balance|"
    r"commit|push|pousse|livre|merge|mr|merge[-\s]request|"
    r"cr[ée]{1,2}[rz]?|ouvre|pr[ée]pare|lance|relance|d[ée]clenche|"
    r"continue|suite|autoris\w*|termine\w*"
    r")\b"
)

# A negation turns the message into a refusal, approval word or not: the
# approval vocabulary holds the verbs themselves, so "ne commit pas" or
# "pas de merge" would otherwise read as a go-ahead. The list is the
# maintainer's; it errs on the safe side ("pas de souci, go" is refused too,
# and the maintainer rephrases). The elided forms count as their full word
# ("n'", "pas d'accord", where "d'accord" is an approval word), with or
# without the apostrophe: a relay sent through `orca terminal send` loses it
# ("ce n est pas"). An apostrophe, straight or curly, ends a word for \b.
NEGATION = (
    r"\bne?\b.*?\bpas\b|"
    r"\bpas\s+de?\b|"
    r"\b(?:non|attends|stop|jamais)\b"
)

SCRATCH_DIRS = ("/private/tmp/claude-", "/tmp/claude-")

# gh subcommands that only read, per command; any other one writes.
GH_READS = {
    "pr": {"list", "view", "status", "diff", "checks", "checkout"},
    "issue": {"list", "view", "status"},
    "repo": {"view", "list", "clone"},
    "run": {"list", "view", "watch", "download"},
    "workflow": {"list", "view"},
    "release": {"list", "view", "download"},
    "label": {"list"},
    "auth": {"status"},
}
# gh commands that only read, whatever follows.
GH_READ_COMMANDS = {"search", "status", "browse", "help", "version", "--version"}
GH_REPO_FLAGS = ("-R", "--repo")
# gh api flags whose value is the next word (so it is not the endpoint).
API_VALUE_FLAGS = {"-H", "--header", "-q", "--jq", "-t", "--template", "--hostname",
                   "--cache", "-p", "--preview", "-R", "--repo"}
API_FIELD_FLAGS = {"-f", "-F", "--field", "--raw-field", "--input"}

# Words that only introduce the real command.
WRAPPERS = {"rtk", "sudo", "command", "exec", "env", "nohup", "time", "if", "then",
            "elif", "else", "while", "until", "do", "!", "{"}
SHELLS = {"sh", "bash", "zsh", "dash"}
# A backtick opens or closes a command substitution: a separator like ( and ).
PUNCT = "();<>|&\n`"


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def last_user_message(transcript_path, max_bytes=20_000_000):
    """Return the maintainer's most recent real message, or None if unreadable.

    Only the tail of the transcript is read: sessions reach tens of megabytes.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    try:
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as handle:
            handle.seek(max(0, size - max_bytes))
            blob = handle.read()
    except Exception:
        return None

    lines = blob.split(b"\n")
    if size > max_bytes:
        lines = lines[1:]  # first line is truncated

    for raw in reversed(lines):
        raw = raw.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
        except Exception:
            continue
        words = maintainer_words(event)
        if words is not None:
            return words
    return None


def maintainer_words(event):
    """The maintainer's own words in one transcript event, or None.

    None means the event is not the maintainer talking (tool result, injected
    notice, `!` command…). A `/` command gives its arguments, "" when it has
    none. Shared with scripts/maintainer_time.py, so both read a transcript
    the same way.
    """
    # Valid JSON that is not an event is skipped like an unreadable line.
    if not isinstance(event, dict) or not isinstance(event.get("message"), dict):
        return None
    # isMeta: harness-injected. isCompactSummary / isVisibleInTranscriptOnly:
    # the session summary written after a context compaction, whose last
    # words ("Continue the conversation…") would read as an approval.
    if (event.get("type") != "user" or event.get("isMeta")
            or event.get("isCompactSummary") or event.get("isVisibleInTranscriptOnly")):
        return None

    content = event["message"].get("content")
    if isinstance(content, list):
        # Tool results are not the maintainer talking (a green light read
        # on a card arrives this way, and does not count).
        if any(isinstance(b, dict) and b.get("type") == "tool_result"
               for b in content):
            return None
        text = "\n".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    elif isinstance(content, str):
        text = content
    else:
        return None

    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S)
    text = re.sub(r"<ide_opened_file>.*?</ide_opened_file>", "", text, flags=re.S)
    text = re.sub(r"<local-command-caveat>.*?</local-command-caveat>", "",
                  text, flags=re.S)
    # Harness-injected notifications are not the maintainer talking.
    # Background task events arrive as "user" messages too; without this
    # they were mistaken for the latest word and blocked an action just
    # approved (a task event kept landing between the "go" and the push).
    text = re.sub(r"<task-notification>.*?</task-notification>", "", text, flags=re.S)
    if ("SYSTEM NOTIFICATION - NOT USER INPUT" in text
            or "<task-notification" in text):
        return None
    # Strip the wrappers the harness adds around the real words, keeping them.
    text = re.sub(r"(?m)^.*The user sent a new message while you were working:\s*$",
                  "", text)
    text = re.sub(
        r"(?m)^\s*(?:UserPromptSubmit hook success:\s*)?(?:\[jam\]\s*)?\[état git\].*$",
        "", text)
    text = text.strip()

    if not text or "[Request interrupted" in text or LOCAL_COMMAND.match(text):
        return None
    if SLASH_COMMAND.match(text):
        args = SLASH_ARGS.search(text)
        return args.group(1).strip() if args else ""
    return text


# --- gh --------------------------------------------------------------------

def simple_commands(cmd):
    """The argv of each simple command, split on ; && || | & ( ) ` and newlines.

    Raises ValueError when the shell text cannot be tokenised (open quote).
    """
    lexer = shlex.shlex(cmd, posix=True, punctuation_chars=PUNCT)
    lexer.whitespace = " \t\r"  # newlines separate commands, see PUNCT
    lexer.whitespace_split = True
    lexer.commenters = ""
    argv = []
    for token in lexer:
        if token and set(token) <= set(PUNCT):
            if argv:
                yield argv
            argv = []
        else:
            argv.append(token)
    if argv:
        yield argv


def strip_wrappers(argv):
    while argv and (re.match(r"[A-Za-z_]\w*=", argv[0]) or argv[0] in WRAPPERS):
        # `rtk proxy <cmd>` runs the raw command behind the RTK hook.
        drop = 2 if argv[0] == "rtk" and argv[1:2] == ["proxy"] else 1
        argv = argv[drop:]
    return argv


def hides_body(flag, value):
    """True when a field's content comes from a file or stdin, out of sight:
    --input, or a typed field (-F/--field) whose value starts with @."""
    if flag == "--input":
        return True
    return flag in ("-F", "--field") and value.split("=", 1)[-1].startswith("@")


def api_reads(args):
    """True for a `gh api` call that only reads (args follow "api")."""
    method, fields, hidden, endpoint = None, False, False, None
    it = iter(args)
    for arg in it:
        if arg in ("-X", "--method"):
            method = next(it, "")
        elif arg.startswith("--method="):
            method = arg.split("=", 1)[1]
        elif arg.startswith("-X"):
            method = arg[2:]
        elif arg in API_FIELD_FLAGS:
            fields = True
            hidden = hides_body(arg, next(it, "")) or hidden
        elif arg.startswith(("--field=", "--raw-field=", "--input=")):
            fields = True
            hidden = hides_body(*arg.split("=", 1)) or hidden
        elif arg[:2] in ("-f", "-F") and len(arg) > 2:
            fields = True
            hidden = hides_body(arg[:2], arg[2:]) or hidden
        elif arg in API_VALUE_FLAGS:
            next(it, None)
        elif not arg.startswith("-") and endpoint is None:
            endpoint = arg
    if endpoint == "graphql":
        # A GraphQL query always comes as a field; only a mutation writes. A
        # query read from a file or stdin cannot be checked: refused by default.
        return not hidden and not re.search(r"\bmutation\b", " ".join(args), re.IGNORECASE)
    return (method or "GET").upper() in ("GET", "HEAD") and not fields


def gh_write(args):
    """'gh <command> <subcommand>' for a gh call that writes, None for a read."""
    words, rest, it = [], [], iter(args)
    for arg in it:
        if arg in GH_REPO_FLAGS:
            next(it, None)
        elif arg.startswith("--repo="):
            continue
        elif arg == "--version" and not words:
            return None
        elif arg.startswith("-"):
            continue
        elif len(words) < 2:
            words.append(arg)
            if words == ["api"]:
                rest = list(it)
                break
    if not words:
        return None  # bare `gh` or `gh --help`: prints help
    command = words[0]
    if command in GH_READ_COMMANDS:
        return None
    if command == "api":
        return None if api_reads(rest) else "gh api"
    sub = words[1] if len(words) > 1 else None
    if sub is None or sub in GH_READS.get(command, ()):
        return None  # `gh pr` alone prints help
    return f"gh {command} {sub}"


def gh_writes(cmd):
    """Labels of the gh writes in a shell command line, in order."""
    try:
        commands = list(simple_commands(cmd))
    except ValueError:
        # Cannot be read safely: any gh in it counts as a write.
        return ["gh (commande non analysable)"] if re.search(r"\bgh\b", cmd) else []
    found = []
    for argv in commands:
        # A quoted word keeps a command substitution whole ("$(gh …)", "`gh …`"):
        # read its text as shell too, before strip_wrappers drops assignments
        # (PR="$(gh pr create)"). The inner words no longer hold the quotes
        # around the substitution, so the recursion ends.
        for word in argv:
            if "$(" in word or "`" in word:
                found.extend(gh_writes(word.replace("`", "\n")))
        argv = strip_wrappers(argv)
        if not argv:
            continue
        name, args = os.path.basename(argv[0]), argv[1:]
        if name in SHELLS:
            flag = next((k for k, a in enumerate(args[:-1])
                         if re.fullmatch(r"-[a-z]*c[a-z]*", a)), None)
            if flag is not None:
                found.extend(gh_writes(args[flag + 1]))
        elif name == "gh":
            label = gh_write(args)
            if label:
                found.append(label)
    return found


# --- verdict -----------------------------------------------------------------

def join_continued_lines(cmd):
    # "gh api \<newline> --method POST …", the multiline form of the GitHub
    # docs: otherwise each line reads as its own command, for the git regexes
    # and for gh_writes alike.
    return re.sub(r"\\\r?\n", " ", cmd)


def git_actions(cmd, cwd):
    """Labels of the git commit and push in a shell command line."""
    # Throwaway repos under the session scratchpad are not real deliveries.
    if any(cwd.startswith(prefix) for prefix in SCRATCH_DIRS):
        return []
    return [label for pattern, label in OUTBOUND
            if re.search(pattern, cmd, re.IGNORECASE)]


def check_approval(matched, transcript_path):
    message = last_user_message(transcript_path)
    if message is None:
        # Cannot verify -> be conservative rather than permissive.
        fail(
            f"[jam] BLOQUÉ : {matched[0]} sans validation vérifiable.\n"
            "Le transcript n'a pas pu être relu. Demande explicitement son accord "
            "au mainteneur avant cette action sortante."
        )

    negated = re.search(NEGATION, message, re.IGNORECASE | re.S)
    if not negated and re.search(APPROVAL, message, re.IGNORECASE):
        return

    excerpt = " ".join(message.split())[:140] or "(commande / sans argument)"
    fail(
        f"[jam] BLOQUÉ : {matched[0]} alors que le mainteneur ne l'a pas validé.\n"
        f"Son dernier message était : « {excerpt} »\n"
        + ("Ce message contient une négation : il vaut refus, même avec un mot d'accord.\n"
           if negated else "")
        + "Règle permanente : commit, push et écritures gh (PR, issues, merge…) "
        "demandent un accord explicite à chaque étape sortante.\n"
        "Annonce ce que tu comptes faire (branche, message de commit, cible) et attends "
        "sa réponse. Ne relance pas la commande avant."
    )


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # A crash would exit 1, which Claude Code treats as a non-blocking error:
    # the command would run. Once a write is recognised, a crash blocks (an
    # approval that cannot be checked is no approval); before, the input is
    # not the payload Claude Code sends, and it lets through like unreadable JSON.
    matched = []
    try:
        if data.get("tool_name") != "Bash":
            sys.exit(0)
        cmd = join_continued_lines((data.get("tool_input") or {}).get("command") or "")
        cwd = data.get("cwd") or "."
        # git first, kept in `matched` even if reading gh crashes.
        matched = git_actions(cmd, cwd)
        matched += gh_writes(cmd)
        if matched:
            check_approval(matched, data.get("transcript_path"))
    except Exception as error:
        if matched:
            fail(
                f"[jam] BLOQUÉ : {matched[0]} sans validation vérifiable.\n"
                f"La garde a planté ({type(error).__name__}). "
                "Demande explicitement son accord au mainteneur avant cette action sortante."
            )
    sys.exit(0)


if __name__ == "__main__":
    main()
