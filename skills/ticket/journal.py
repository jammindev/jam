#!/usr/bin/env python3
"""The ticket journal: a ticket's memory outside the conversation.

The model writes the content; this script owns the format and computes everything
that has exactly one correct answer (ticket key, journal path, next stage, whether
to clear the conversation first). Behaviour is specified in docs/specs/journal.md.
Python 3.9+, standard library only.
"""

import argparse
import contextlib
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

GIT_TIMEOUT = 3
STAGE_TIMEOUT = 5
PR_TIMEOUT = 20
RESUME_MAX_LINES = 30
NONE = "(none)"

# Declared once: adding a stage only changes this table. The flag says whether the
# conversation is cleared before entering the stage, so that review and acceptance
# judge the work by the ticket, not by what the coding session meant to do.
STAGES = [("framing", False), ("code", False), ("review", True),
          ("acceptance", True), ("delivery", False), ("follow-up", False)]
STAGE_NAMES = [name for name, _ in STAGES]
CLOSED = "closed"

FIELDS = ["Stage", "Size", "Sensitive", "Branch", "Worktree", "PR", "Updated"]
SECTIONS = ["Goal", "Done when", "Plan", "Decisions", "Resume here", "Lessons", "Log"]
SIZES = ["small", "medium"]  # "large" comes with its workflow
YES_NO = ["yes", "no"]
VERDICTS = ["seen", "corrected", "explained"]

DEFAULT_PATTERN = r"(?:^|/)(\d+)(?=-|$)"
FIELD_LINE = re.compile(r"^- \*\*(.+?)\*\*: ?(.*)$")
STOP_IMITATION = re.compile(r"^stop at \S+.*:\s*(seen|corrected|explained)\b", re.IGNORECASE)
STOP_LINE = re.compile(r"^Stop at \S+(?: \([^()]*\))?: (seen|corrected|explained)(, .*)?$")


class JamError(Exception):
    """A refusal or error explained to the user, who sees only its message."""


# --- git and context ---------------------------------------------------------

def git(cwd, *args):
    """Run git; return stripped stdout, or None when it fails or is missing."""
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False,
                                text=True, encoding="utf-8", timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def sanitize(value, lower=False):
    """Keep [A-Za-z0-9_.-]; so a key or repo-id can never hold `/` or start with `.`."""
    value = re.sub(r"[^A-Za-z0-9_.-]", "-", value.lower() if lower else value)
    return re.sub(r"-+", "-", value).strip("-.")


def remote_path(url):
    """The path part of a remote URL: no scheme, user, host or port."""
    scheme = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://[^/]*(.*)$", url)
    if scheme:
        return scheme.group(1)
    scp = re.match(r"^(?:[^@/]+@)?[^:/]+:(.*)$", url)
    return scp.group(1) if scp else url


def compute_repo_id(cwd):
    url = git(cwd, "remote", "get-url", "origin")
    if url:
        path = re.sub(r"\.git$", "", remote_path(url).rstrip("/"))
        raw = "-".join(part for part in path.split("/") if part)
    else:
        # No remote: the directory name alone would collide, so a hash of the
        # shared git directory (the same from every worktree) tells repos apart.
        common = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if not common:
            raise JamError("cannot find the repository's git directory")
        common = os.path.realpath(common)
        # Asked of the shared directory: a linked worktree of a bare repo says "false".
        bare = git(cwd, f"--git-dir={common}", "rev-parse", "--is-bare-repository") == "true"
        main = common if bare else os.path.dirname(common)
        digest = hashlib.sha1(common.encode("utf-8")).hexdigest()[:6]
        raw = f"{os.path.basename(main)}-{digest}"
    repo_id = sanitize(raw, lower=True)
    if not repo_id:
        raise JamError("cannot derive a repository id")
    return repo_id


def parse_fields(path):
    """Read `- **Field**: value` lines; a pair of backticks around a value goes."""
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FIELD_LINE.match(line)
        if match and match.group(1) not in values:
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] == "`":
                value = value[1:-1]
            values[match.group(1)] = value
    return values


class Context:
    """Everything known about the repository and the checkout given by --cwd."""

    def __init__(self, cwd, quiet=False, pattern=None):
        self.toplevel = git(cwd, "rev-parse", "--show-toplevel")
        if not self.toplevel:
            raise JamError("not inside a git repository")
        self.branch = git(cwd, "symbolic-ref", "--quiet", "--short", "HEAD")
        self.repo_id = compute_repo_id(cwd)
        home = os.environ.get("JAM_HOME") or os.path.join(Path.home(), ".jam")
        self.home = Path(home) / self.repo_id
        self.project, self.project_files = {}, []
        shared = Path(self.toplevel) / ".jam" / "project.md"
        for path, personal in ((shared, False), (self.home / "project.md", True)):
            if not path.is_file():
                continue
            values = parse_fields(path)
            # Stage command runs unseen on every stage change: never from a file
            # that arrives with the branch, only from the user's own file.
            if not personal and values.pop("Stage command", None) and not quiet:
                print(f"jam: warning: 'Stage command' in {path} is ignored; "
                      "set it in the personal project file", file=sys.stderr)
            self.project.update(values)
            self.project_files.append(str(path))
        # An explicit pattern (key --pattern) replaces the files' one before it is
        # compiled, so a broken pattern in a file never blocks proving its fix.
        self.use_pattern(pattern if pattern is not None else self.project.get("Ticket pattern"))

    def use_pattern(self, pattern):
        try:
            self.pattern = re.compile(pattern or DEFAULT_PATTERN, re.IGNORECASE)
        except re.error as exc:
            raise JamError(f"invalid Ticket pattern {pattern!r}: {exc}") from None

    def branch_key(self):
        """The key the current branch resolves to, or None (detached HEAD)."""
        if not self.branch:
            return None
        match = self.pattern.search(self.branch)
        raw = match and (match.group(1) if self.pattern.groups else match.group(0))
        return sanitize(raw or self.branch).upper() or None

    def resolve_key(self, explicit):
        if explicit is not None:
            key = sanitize(explicit).upper()
            if not key:
                raise JamError(f"invalid key {explicit!r}")
            return key
        key = self.branch_key()
        if not key:
            raise JamError(f"no key from branch {self.branch!r}: pass --key"
                           if self.branch else "detached HEAD: pass --key")
        return key

    def journal(self, key):
        return self.home / "journals" / f"{key}.md"

    def archive(self, key):
        return self.home / "archive" / f"{key}.md"

    def default_branches(self):
        ref = git(self.toplevel, "symbolic-ref", "--quiet", "--short",
                  "refs/remotes/origin/HEAD")
        return {ref.split("/", 1)[1]} if ref and "/" in ref else {"main", "master"}


# --- journal format ----------------------------------------------------------

class Journal:
    def __init__(self, key, title, fields, sections):
        self.key, self.title = key, title
        self.fields, self.sections = fields, sections

    @classmethod
    def parse(cls, text):
        lines = text.splitlines()
        head = re.match(r"^# (.+?) · (.*)$", lines[0] if lines else "")
        if not head:
            raise JamError("journal has no title line")
        fields, sections, current = {}, {name: [] for name in SECTIONS}, None
        for line in lines[1:]:
            title = line[3:].strip() if line.startswith("## ") else None
            if title in SECTIONS:
                current = title
            elif current:
                sections[current].append(line)
            else:
                match = FIELD_LINE.match(line)
                if match:
                    fields[match.group(1)] = match.group(2)
        return cls(head.group(1), head.group(2), fields,
                   {name: "\n".join(body).strip("\n") for name, body in sections.items()})

    def render(self):
        out = [f"# {self.key} · {self.title}", ""]
        out += [f"- **{name}**: {self.fields.get(name, NONE)}" for name in FIELDS]
        for name in SECTIONS:
            out += ["", f"## {name}"] + ([self.sections[name]] if self.sections[name] else [])
        return "\n".join(out) + "\n"

    def items(self, section):
        return [line[2:] for line in self.sections[section].splitlines()
                if line.startswith("- ")]

    def append(self, section, text):
        body = self.sections[section]
        self.sections[section] = f"{body}\n- {text}" if body else f"- {text}"

    def log(self, text):
        self.append("Log", f"{now()} · {text}")

    def first_line(self, section):
        return next((line for line in self.sections[section].splitlines() if line.strip()), "")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load(path):
    if not path.is_file():
        raise JamError(f"no journal at {path}")
    return Journal.parse(path.read_text(encoding="utf-8"))


def write_atomic(path, text):
    """Write through a temporary file in the same directory, then os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --- input rules -------------------------------------------------------------

def one_line(value, name):
    value = " ".join(value.split())
    if not value:
        raise JamError(f"--{name} is empty")
    return value


def multi_line(value, name):
    value = "\n".join(value.splitlines()).strip()  # every line separator becomes \n
    if not value:
        raise JamError(f"--{name} is empty")
    # A line starting with `#` could be read back as a section title.
    if any(line.lstrip().startswith("#") for line in value.splitlines()):
        raise JamError(f"--{name} has a line starting with '#'")
    return value


def decision(value):
    value = one_line(value, "decision")
    if STOP_IMITATION.match(value):
        raise JamError("a decision cannot imitate a stop line; record the user's answer "
                       "with: journal.py stop <seen|corrected|explained> [--about ...] "
                       "[--note ...]")
    return value


def plural(count, word):
    return f"+{count} {word}" + ("" if count == 1 else "s")


# --- commands ----------------------------------------------------------------

def run_command(command, journal, ctx, timeout, output=subprocess.PIPE):
    """Run a project-file command; values reach it only as environment variables."""
    known = {name: "" if journal.fields[name] == NONE else journal.fields[name]
             for name in ("PR", "Worktree")}
    env = dict(os.environ, JAM_KEY=journal.key, JAM_STAGE=journal.fields["Stage"],
               JAM_REPO=ctx.repo_id, JAM_PR=known["PR"], JAM_WORKTREE=known["Worktree"],
               JAM_RESUME=journal.first_line("Resume here"))
    return subprocess.run(["/bin/sh", "-c", command], cwd=ctx.toplevel, env=env,
                          stdout=output, stderr=output, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, check=False)


def stage_command(journal, ctx):
    """Let an outside tool (a terminal title, a task board) follow the ticket; never fails."""
    command = ctx.project.get("Stage command")
    if not command or journal.fields["Worktree"] == NONE:
        return
    try:
        run_command(command, journal, ctx, STAGE_TIMEOUT, output=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


def cmd_key(ctx, args):
    # --branch and --pattern let `init` prove a pattern before writing it.
    if args.branch is not None:
        ctx.branch = args.branch
    key = ctx.resolve_key(args.key)
    # The main worktree's git dir is the shared one; a linked worktree has its own.
    git_dirs = [git(ctx.toplevel, "rev-parse", "--path-format=absolute", flag)
                for flag in ("--git-dir", "--git-common-dir")]
    if None in git_dirs:
        raise JamError("cannot find the repository's git directory")
    git_dirs = [os.path.realpath(path) for path in git_dirs]
    main_worktree = "yes" if git_dirs[0] == git_dirs[1] else "no"
    rows = [("key", key), ("branch", ctx.branch or ""), ("worktree", ctx.toplevel),
            ("main_worktree", main_worktree), ("repo", ctx.repo_id), ("journal", ctx.journal(key)),
            ("exists", "yes" if ctx.journal(key).is_file() else "no"),
            ("archived", "yes" if ctx.archive(key).is_file() else "no"),
            ("project_files", ":".join(ctx.project_files)),
            ("reports", ctx.home / "reports" / key)]
    print("\n".join(f"{name}={value}" for name, value in rows))


def cmd_init(ctx, args):
    values = {name: one_line(args.title, "title") if name == "title"
              else multi_line(getattr(args, name), name.replace("_", "-"))
              for name in ("title", "goal", "done_when", "resume")}
    plan = multi_line(args.plan, "plan") if args.plan is not None else ""
    if args.key is None and ctx.branch in ctx.default_branches():
        raise JamError(f"'{ctx.branch}' is the default branch: pass --key")
    key = ctx.resolve_key(args.key)
    if ctx.archive(key).is_file():
        raise JamError(f"an archived journal exists for {key}: {ctx.archive(key)}")
    if ctx.journal(key).is_file() and not args.force:
        raise JamError(f"a journal exists for {key}: {ctx.journal(key)} (--force replaces it)")
    # Branch and Worktree are recorded only from a checkout of this very ticket.
    here = ctx.branch_key() == key
    journal = Journal(key, values["title"], {
        "Stage": STAGE_NAMES[0], "Size": args.size, "Sensitive": args.sensitive,
        "Branch": ctx.branch if here else NONE, "Worktree": ctx.toplevel if here else NONE,
        "PR": NONE, "Updated": now()}, {name: "" for name in SECTIONS})
    journal.sections.update({"Goal": values["goal"], "Done when": values["done_when"],
                             "Plan": plan, "Resume here": values["resume"]})
    journal.log(f"created at {STAGE_NAMES[0]}")
    write_atomic(ctx.journal(key), journal.render())
    print(ctx.journal(key))
    stage_command(journal, ctx)


def cmd_show(ctx, args):
    sys.stdout.write(load(ctx.journal(ctx.resolve_key(args.key))).render())


def cmd_set(ctx, args):
    texts = {"goal": "Goal", "done_when": "Done when", "plan": "Plan",
             "resume": "Resume here"}
    if all(value in (None, []) for name, value in vars(args).items()
           if name not in ("command", "key", "cwd")):
        raise JamError("set needs at least one option")
    # Every value is checked before the journal is touched.
    title = one_line(args.title, "title") if args.title is not None else None
    pr = one_line(args.pr, "pr") if args.pr is not None else None
    sections = {texts[name]: multi_line(getattr(args, name), name.replace("_", "-"))
                for name in texts if getattr(args, name) is not None}
    decisions = [decision(value) for value in args.decision]
    lessons = [one_line(value, "lesson") for value in args.lesson]
    logs = [one_line(value, "log") for value in args.log]

    key = ctx.resolve_key(args.key)
    journal = load(ctx.journal(key))
    old_stage, old_resume = journal.fields["Stage"], journal.sections["Resume here"]
    stage_changed = args.stage is not None and args.stage != old_stage
    if stage_changed:
        journal.fields["Stage"] = args.stage
    for name, value in (("Size", args.size), ("Sensitive", args.sensitive), ("PR", pr)):
        if value is not None:
            journal.fields[name] = value
    if title is not None:
        journal.title = title
    journal.sections.update(sections)
    for text in decisions:
        journal.append("Decisions", text)
    for text in lessons:
        journal.append("Lessons", text)
    if ctx.branch_key() == key:  # a call from main with --key keeps the ticket's branch
        journal.fields["Branch"], journal.fields["Worktree"] = ctx.branch, ctx.toplevel
    journal.fields["Updated"] = now()

    parts = []
    if stage_changed:
        suffix = f" ({plural(len(decisions), 'decision')})" if decisions else ""
        parts.append(f"{old_stage} → {args.stage}{suffix}")
    elif decisions:
        parts.append(plural(len(decisions), "decision"))
    if pr is not None:
        parts.append(f"PR {pr}")
    parts += logs
    if parts:
        journal.log(" · ".join(parts))
    write_atomic(ctx.journal(key), journal.render())
    if stage_changed or journal.sections["Resume here"] != old_resume:
        stage_command(journal, ctx)


def cmd_stop(ctx, args):
    about = one_line(args.about, "about") if args.about is not None else None
    note = one_line(args.note, "note") if args.note is not None else None
    if about and ("(" in about or ")" in about):
        raise JamError("--about cannot contain parentheses")
    if args.verdict == "corrected" and not note:
        raise JamError("a corrected stop needs --note: what the user changed")
    key = ctx.resolve_key(args.key)
    journal = load(ctx.journal(key))
    stage = journal.fields["Stage"]
    # Parseable on purpose: the share of `corrected` stops measures rework.
    line = f"Stop at {stage}" + (f" ({about})" if about else "") + f": {args.verdict}"
    journal.append("Decisions", line + (f", {note}" if note else ""))
    journal.log(f"stop at {stage}: {args.verdict}")
    journal.fields["Updated"] = now()
    write_atomic(ctx.journal(key), journal.render())


def cmd_next(ctx, args):
    journal = load(ctx.journal(ctx.resolve_key(args.key)))
    current = journal.fields["Stage"]
    if current not in STAGE_NAMES:
        raise JamError(f"unknown stage {current!r}")
    index = STAGE_NAMES.index(current)
    if index + 1 == len(STAGES):
        print(f"current={current}\nnext={CLOSED}\nclear_first=no\n"
              "hint=run close once the PR is merged")
        return
    name, clear = STAGES[index + 1]
    clear = clear and journal.fields.get("Size") != "small"
    print(f"current={current}\nnext={name}\nclear_first={'yes' if clear else 'no'}")


def is_routine_stop(text):
    match = STOP_LINE.match(text)
    return bool(match) and match.group(1) != "corrected" and not match.group(2)


def cmd_resume(ctx, args):
    path = ctx.journal(ctx.resolve_key(args.key))
    if not path.is_file():
        return
    journal = load(path)
    status = f"Stage: {journal.fields['Stage']} · Size: {journal.fields['Size']}"
    if journal.fields.get("PR", NONE) != NONE:
        status += f" · PR: {journal.fields['PR']}"
    decisions = [d for d in journal.items("Decisions") if not is_routine_stop(d)][-3:]
    head = [f"# {journal.key} · {journal.title}", status,
            f"Goal: {journal.first_line('Goal')}"]
    if decisions:
        head += ["Recent decisions:"] + [f"- {d}" for d in decisions]
    head.append("Resume here:")
    tail = [f"Journal: {path}",
            "Update the journal (journal.py set) before any /clear."]
    resume = journal.sections["Resume here"].splitlines()
    room = RESUME_MAX_LINES - len(head) - len(tail)
    if len(resume) > room:
        resume = resume[:max(room - 1, 0)] + ["…"]
    sys.stdout.write("\n".join(head + resume + tail) + "\n")


def cmd_list(ctx, args):
    folder = ctx.home / "journals"
    paths = sorted(folder.glob("*.md")) if folder.is_dir() else []
    if not paths:
        print("no journal")
        return
    rows = [("KEY", "STAGE", "PR", "UPDATED")]
    for path in paths:
        journal = load(path)
        rows.append((journal.key, *(journal.fields.get(name, NONE)
                                    for name in ("Stage", "PR", "Updated"))))
    widths = [max(len(row[i]) for row in rows) for i in range(3)]
    for row in rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)) + "  " + row[3])


def gather_jam_lessons(journal, ctx, key, day):
    """Copy the lessons about jam itself to one file, across every repository.

    They belong to jam, not to the project: the journal keeps their context, and jam's
    maintainer reads this file instead of every journal. `jam: nothing to report` only
    tells, in the journal, a silent answer from a forgotten question: it is not copied.
    Lessons are one line each (`set --lesson` flattens them). Never fails the close.
    """
    lessons = [item.strip() for item in journal.items("Lessons")
               if item.strip().lower().startswith("jam:")
               and item.strip().lower() != "jam: nothing to report"]
    if not lessons:
        return
    text = "".join(f"- {day} · {ctx.repo_id}#{key} · {lesson}\n" for lesson in lessons)
    try:
        with open(ctx.home.parent / "jam-lessons.md", "a", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as exc:
        print(f"jam: warning: lessons about jam not gathered: {exc}", file=sys.stderr)


def cmd_close(ctx, args):
    pending = [one_line(value, "pending") for value in args.pending]
    key = ctx.resolve_key(args.key)
    if ctx.archive(key).is_file():
        raise JamError(f"an archived journal exists for {key}: {ctx.archive(key)}")
    journal = load(ctx.journal(key))
    if not args.force:
        command = ctx.project.get("PR state command")
        if journal.fields["PR"] == NONE:
            raise JamError("the journal has no PR (set --pr, or close --force)")
        if not command:
            raise JamError("no 'PR state command' in the project file "
                           "(close --force skips the check)")
        try:
            result = run_command(command, journal, ctx, PR_TIMEOUT)
        except subprocess.TimeoutExpired:
            raise JamError("the PR state command timed out") from None
        if result.returncode != 0:
            detail = (result.stderr.strip().splitlines() or [""])[-1]
            raise JamError(f"the PR state command failed (exit {result.returncode}) {detail}")
        state = result.stdout.strip().lower()
        if state != "merged":
            raise JamError(f"the PR is not merged (state: {state or 'empty'})")
    day = f"{datetime.now():%Y-%m-%d}"
    journal.fields["Stage"] = CLOSED
    journal.sections["Resume here"] = "\n".join(
        [f"Closed on {day}."] + [f"- {item}" for item in pending])
    journal.log(f"closed{' (forced)' if args.force else ''} · {len(pending)} pending")
    journal.fields["Updated"] = now()
    # Written in place, then moved: if the move fails, the journal stays active at
    # `closed` and a second `close` finishes the job.
    write_atomic(ctx.journal(key), journal.render())
    ctx.archive(key).parent.mkdir(parents=True, exist_ok=True)
    os.replace(ctx.journal(key), ctx.archive(key))
    print(f"archived={ctx.archive(key)}")
    gather_jam_lessons(journal, ctx, key, day)
    if journal.fields["Worktree"] != NONE:
        print(f"worktree={journal.fields['Worktree']} (ask the user before removing it)")
    stage_command(journal, ctx)


# --- command line ------------------------------------------------------------

WRITES = {"init", "set", "stop", "close"}


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--key")
    common.add_argument("--cwd", default=".")
    parser = argparse.ArgumentParser(prog="journal.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("show", "next", "resume", "list"):
        sub.add_parser(name, parents=[common])
    key = sub.add_parser("key", parents=[common])
    key.add_argument("--branch")
    key.add_argument("--pattern")
    init = sub.add_parser("init", parents=[common])
    for option in ("--title", "--goal", "--done-when", "--resume"):
        init.add_argument(option, required=True)
    init.add_argument("--plan")
    init.add_argument("--size", choices=SIZES, default="medium")
    init.add_argument("--sensitive", choices=YES_NO, default="no")
    init.add_argument("--force", action="store_true")
    set_ = sub.add_parser("set", parents=[common])
    set_.add_argument("--stage", choices=STAGE_NAMES)
    for option in ("--title", "--goal", "--done-when", "--plan", "--resume", "--pr"):
        set_.add_argument(option)
    set_.add_argument("--size", choices=SIZES)
    set_.add_argument("--sensitive", choices=YES_NO)
    for option in ("--decision", "--lesson", "--log"):
        set_.add_argument(option, action="append", default=[])
    stop = sub.add_parser("stop", parents=[common])
    stop.add_argument("verdict", choices=VERDICTS)
    stop.add_argument("--about")
    stop.add_argument("--note")
    close = sub.add_parser("close", parents=[common])
    close.add_argument("--pending", action="append", default=[])
    close.add_argument("--force", action="store_true")
    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["resume"]:
        # The session-start hook: it never fails and never blocks a session.
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                args = build_parser().parse_args(argv)
            cmd_resume(Context(args.cwd, quiet=True), args)
        except BaseException:  # silence is the contract of the hook
            pass
        return 0
    args = build_parser().parse_args(argv)
    try:
        ctx = Context(args.cwd, pattern=getattr(args, "pattern", None))
        globals()[f"cmd_{args.command}"](ctx, args)
    except (JamError, OSError) as exc:
        suffix = "; nothing was written" if args.command in WRITES else ""
        print(f"jam: {exc}{suffix}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
