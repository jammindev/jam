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
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
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
# Stats is written by `close` only: it exists in archived journals, and in an active one
# left at `closed` when the move to the archive failed.
SECTIONS = ["Goal", "Done when", "Plan", "Decisions", "Resume here", "Lessons", "Stats",
            "Log"]
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
            if name == "Stats" and not self.sections[name]:
                continue  # never rendered empty: an active journal has no stats
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


def gather_jam_lessons(journal, ctx, key, day, extra=()):
    """Copy the lessons about jam itself to one file, across every repository.

    They belong to jam, not to the project: the journal keeps their context, and jam's
    maintainer reads this file instead of every journal. `jam: nothing to report` only
    tells, in the journal, a silent answer from a forgotten question: it is not copied.
    Lessons are one line each (`set --lesson` flattens them). Never fails the close.
    """
    lessons = [item.strip() for item in journal.items("Lessons")
               if item.strip().lower().startswith("jam:")
               and item.strip().lower() != "jam: nothing to report"]
    lessons += list(extra)  # what close itself noticed about jam (stats it could not read)
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
    # The figures are recorded now: transcripts do not last. Replaces the section a
    # previous close may have written before its move failed.
    body, tr, diff_reason = compute_stats(journal, ctx, datetime.now(timezone.utc))
    journal.sections["Stats"] = body
    # Written in place, then moved: if the move fails, the journal stays active at
    # `closed` and a second `close` finishes the job.
    write_atomic(ctx.journal(key), journal.render())
    ctx.archive(key).parent.mkdir(parents=True, exist_ok=True)
    os.replace(ctx.journal(key), ctx.archive(key))
    print(f"archived={ctx.archive(key)}")
    problem = stats_problem(tr)
    if problem:
        print(problem, file=sys.stderr)
    if diff_reason and diff_reason.startswith(("PR size command", "unexpected output")):
        # The project file is at fault, not jam: shown, never gathered.
        print(f"jam: Diff unavailable: {diff_reason}", file=sys.stderr)
    # Written after the move, with the lessons: a second close cannot repeat it.
    gather_jam_lessons(journal, ctx, key, day, extra=[problem] if problem else [])
    if journal.fields["Worktree"] != NONE:
        print(f"worktree={journal.fields['Worktree']} (ask the user before removing it)")
    stage_command(journal, ctx)


# --- stats -------------------------------------------------------------------
# A ticket's figures, from its journal and from Claude Code's transcripts. The
# transcript format belongs to Claude Code and changes without notice: everything that
# reads it lives in read_transcripts and below, and degrades instead of raising.

ASK_TOOLS = {"AskUserQuestion", "ExitPlanMode"}
# Text a user entry starts with when it is not the user stepping in.
NOT_PROMPTS = ("<task-notification>", "<local-command", "<command-name>", "<command-message>",
               "<bash-input>", "<bash-stdout>", "<bash-stderr>",
               "[Request interrupted by user")  # Escape: the next message is the prompt
CLEAR = "<command-name>/clear</command-name>"
EFFORTS = ("low", "medium", "high", "xhigh", "max")  # weakest first, for reading
TOKEN_FIELDS = ("output_tokens", "input_tokens", "cache_creation_input_tokens",
                "cache_read_input_tokens")
REVIEW_PART = re.compile(r"review: (\d+) blocking, (\d+) other\b")
INNER_PARENS = re.compile(r"\s*\([^()]*\)")


class Transcripts:
    """What the transcripts tell; `problem` is None or (unavailable|suspect, reason)."""

    def __init__(self, problem=None):
        self.problem = problem
        self.agent_seconds, self.prompts, self.answers = 0.0, 0, 0
        self.compactions = self.auto_compactions = self.clears = 0
        self.runs, self.tokens, self.versions, self.first = {}, {}, set(), None


def transcripts_root():
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(config) if config else Path.home() / ".claude"


def entry_time(entry):
    try:
        stamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    return stamp if stamp.tzinfo else None


def read_entries(path):
    """The entries of a JSONL transcript that have a usable timestamp, sorted by it."""
    entries = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if isinstance(entry, dict) and entry_time(entry):
                entries.append(entry)
    return sorted(entries, key=entry_time)


def inside(path, worktree):
    path = os.path.realpath(path)
    return path == worktree or path.startswith(worktree.rstrip("/") + "/")


def user_text(content):
    """(text, has_image) of a user message's content; text is None if not a message."""
    if isinstance(content, str):
        return content, False
    if not isinstance(content, list):
        return None, False
    blocks = [block for block in content if isinstance(block, dict)]
    text = "".join(b["text"] for b in blocks
                   if b.get("type") == "text" and isinstance(b.get("text"), str))
    return text, any(b.get("type") == "image" for b in blocks)


def classify(entry, asks, main):
    """prompt, answer, notification, work, or None (neutral). See the spec, `stats`."""
    kind = entry.get("type")
    message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
    content = message.get("content")
    if kind == "assistant":
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_use" \
                    and block.get("name") in ASK_TOOLS:
                asks.add(block.get("id"))
        return "work"
    if kind == "attachment":
        attachment = entry.get("attachment") if isinstance(entry.get("attachment"), dict) else {}
        origin = attachment.get("origin") if isinstance(attachment.get("origin"), dict) else {}
        typed_meanwhile = attachment.get("type") == "queued_command" \
            and origin.get("kind") == "human"
        return "prompt" if typed_meanwhile and main else None
    if kind != "user" or entry.get("isCompactSummary"):
        return None
    blocks = content if isinstance(content, list) else []
    results = [b for b in blocks if isinstance(b, dict) and b.get("type") == "tool_result"]
    if results:
        decision = entry.get("permissionDecision")
        # The user granted or refused a permission: the agent was waiting for them.
        asked = isinstance(decision, dict) and decision.get("source") == "user_temporary" \
            or entry.get("toolUseResult") == "User rejected tool use"
        return "answer" if asked or any(b.get("tool_use_id") in asks for b in results) \
            else "work"
    text, image = user_text(content)
    # A subagent's first entry is its parent's request, never the user.
    if main and not entry.get("isMeta") and entry.get("promptSource") != "system" \
            and (text or image) and not (text or "").startswith(NOT_PROMPTS):
        return "prompt"
    return "notification"  # it often arrives after hours: it must end a wait


def union_seconds(intervals):
    """Total length covered by the intervals, overlaps counted once: a reviewer working
    in the background while the main session waits must not double the time."""
    total, current = 0.0, None
    for start, end in sorted(intervals):
        if current and start <= current[1]:
            current = (current[0], max(current[1], end))
            continue
        if current:
            total += (current[1] - current[0]).total_seconds()
        current = (start, end)
    if current:
        total += (current[1] - current[0]).total_seconds()
    return total


class Reader:
    """Accumulates the counted entries of every transcript of one ticket."""

    def __init__(self, bound):
        self.bound, self.out = bound, Transcripts()
        self.seen, self.usage, self.group = set(), {}, {}
        self.intervals, self.assistants = [], 0

    def once(self, entry):
        """True the first time an entry is met: a forked session repeats its uuids."""
        uuid = entry.get("uuid")
        if not isinstance(uuid, str):
            return True
        if uuid in self.seen:
            return False
        self.seen.add(uuid)
        return True

    def scan(self, entries, agent):
        """Count one transcript; return whether any of its entries was counted."""
        out, asks, kept, any_counted = self.out, set(), [], False
        for entry in entries:
            stamp = entry_time(entry)
            if self.bound and stamp > self.bound:
                continue
            any_counted = True
            if isinstance(entry.get("version"), str):
                out.versions.add(entry["version"])
            kind = classify(entry, asks, agent == "main")
            if entry.get("type") == "assistant":
                self.add_usage(entry, agent)
            if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary" \
                    and self.once(entry):
                meta = entry.get("compactMetadata")
                out.compactions += 1
                out.auto_compactions += isinstance(meta, dict) and meta.get("trigger") == "auto"
                continue
            if kind is None:
                continue
            kept.append((stamp, kind))
            out.first = min(out.first, stamp) if out.first else stamp
            if not self.once(entry):
                continue
            out.prompts += kind == "prompt"
            out.answers += kind == "answer"
            text, _ = user_text((entry.get("message") or {}).get("content")) \
                if entry.get("type") == "user" and isinstance(entry.get("message"), dict) \
                else (None, False)
            out.clears += bool(text and text.startswith(CLEAR))
        # Busy while the model answers or a foreground tool runs: a gap ending in work.
        self.intervals += [(a, b) for (a, _), (b, kind) in zip(kept, kept[1:])
                           if kind == "work"]
        return any_counted

    def add_usage(self, entry, agent):
        self.assistants += 1
        message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
        usage, mid, model = message.get("usage"), message.get("id"), message.get("model")
        if not isinstance(usage, dict) or not isinstance(mid, str) or model == "<synthetic>":
            return
        # A message written over several lines carries partial counts on the first ones.
        # A value of the wrong type is skipped, keeping what was already seen.
        previous = self.usage.get(mid, {})
        self.usage[mid] = {f: max(previous.get(f, 0),
                                  usage[f] if isinstance(usage.get(f), int) else 0)
                           for f in TOKEN_FIELDS}
        # The effort is the setting a ticket's size may one day choose: kept to compare.
        effort = entry.get("effort") if isinstance(entry.get("effort"), str) else None
        self.group.setdefault(mid, (agent, model if isinstance(model, str) else "unknown",
                                    effort or None))

    def finish(self):
        out = self.out
        out.agent_seconds = union_seconds(self.intervals)
        for mid, usage in self.usage.items():
            totals = out.tokens.setdefault(self.group[mid], [0] * len(TOKEN_FIELDS))
            for i, name in enumerate(TOKEN_FIELDS):
                totals[i] += usage.get(name, 0)
        # Checked across the whole ticket: an empty session on its own is normal.
        reasons = [reason for reason, missing in (
            ("no assistant entry", not self.assistants), ("no usage", not self.usage),
            ("no busy interval", not self.intervals)) if missing]
        if reasons:
            out.problem = ("suspect", "; ".join(reasons))
        return out


def read_transcripts(worktree, bound):
    """The ticket's transcript figures; never raises."""
    try:
        worktree = os.path.realpath(worktree)
        # Claude Code's naming, observed and not documented; the cwd check decides.
        folder = transcripts_root() / "projects" / re.sub(r"[^A-Za-z0-9]", "-", worktree)
        if not folder.is_dir():
            return Transcripts(("unavailable", "no transcript"))
        reader, belongs, done = Reader(bound), False, set()
        for path in sorted(folder.glob("*.jsonl")):
            entries = read_entries(path)
            located = [e for e in entries if isinstance(e.get("cwd"), str)]
            if not located or not inside(located[0]["cwd"], worktree):
                continue
            if any(e.get("entrypoint") == "sdk-cli" for e in entries):
                continue  # another program calling Claude Code, such as a chat namer
            belongs = True
            reader.scan(entries, "main")
            for sub in sorted((path.parent / path.stem / "subagents").glob("agent-*.jsonl")):
                if sub.name in done:
                    continue
                done.add(sub.name)
                try:
                    meta = json.loads(sub.with_suffix(".meta.json").read_text(encoding="utf-8"))
                    agent = meta.get("agentType") or "unknown"
                except (OSError, ValueError, AttributeError):
                    agent = "unknown"
                if reader.scan(read_entries(sub), str(agent)):
                    reader.out.runs[str(agent)] = reader.out.runs.get(str(agent), 0) + 1
        if not belongs:
            return Transcripts(("unavailable", "no session in the worktree"))
        return reader.finish()
    except Exception as exc:  # the format moved: degrade, never fail a close
        return Transcripts(("unavailable", f"unreadable transcripts: {one_line_error(exc)}"))


def one_line_error(exc):
    """An exception as one line: the Stats section has a fixed line format."""
    return " ".join(f"{type(exc).__name__}: {exc}".split())[:160]


def log_entries(journal):
    """(local time, text) of every log line."""
    out = []
    for item in journal.items("Log"):
        stamp, _, text = item.partition(" · ")
        try:
            out.append((datetime.strptime(stamp, "%Y-%m-%d %H:%M"), text))
        except ValueError:
            continue
    return out


def journal_figures(journal):
    """The figures the journal alone gives."""
    entries = log_entries(journal)
    created = next((t for t, text in entries if text.startswith("created at ")), None)
    closed = [t for t, text in entries if text.split(" · ")[0] in ("closed", "closed (forced)")]
    stops = [STOP_LINE.match(item) for item in journal.items("Decisions")]
    stops = [match.group(1) for match in stops if match]
    blocking = other = logged = 0
    for _, text in entries:
        for part in text.split(" · "):
            # Details in parentheses, possibly nested, go before matching.
            stripped = None
            while stripped != part:
                stripped, part = part, INNER_PARENS.sub("", part)
            match = REVIEW_PART.match(part)
            if match:
                blocking, other = blocking + int(match.group(1)), other + int(match.group(2))
                logged += 1
    return {"created": created, "closed": closed[-1] if closed else None,
            "stops": (stops.count("corrected"), len(stops)),
            "findings": (blocking, other, logged)}


def archive_bound(closed):
    """Start of the minute of the close (a local time from the log), as UTC: the exchange
    that follows a close falls in the same minute, the close's own turn is the price."""
    return closed.astimezone(timezone.utc)


def half_up(value, places=0):
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def duration(seconds):
    total = int(half_up(seconds / 60))
    if total < 60:
        return f"{total} min"
    if total < 1440:
        return f"{total // 60} h {total % 60:02d}"
    return f"{total // 1440} d {total % 1440 // 60} h"


def token_count(count):
    if count < 1000:
        return str(count)
    # The unit is chosen after rounding: 999 600 is 1.0M, never 1000k.
    if half_up(count / 1000, 1) < 100:
        return f"{half_up(count / 1000, 1)}k"
    if half_up(count / 1000) < 1000:
        return f"{half_up(count / 1000)}k"
    return f"{half_up(count / 1_000_000, 1)}M"


def quantity(number, word):
    return f"{number} {word}" + ("" if number == 1 else "s")


def version_range(versions):
    def numeric(version):
        return [int(part) for part in re.findall(r"\d+", version)]
    ordered = sorted(versions, key=numeric)
    if not ordered:
        return None
    return ordered[0] if len(ordered) == 1 else f"{ordered[0]}–{ordered[-1]}"


def diff_figure(journal, ctx):
    """(text, None) or (None, reason): the ticket's size, from its PR."""
    command = ctx.project.get("PR size command")
    if journal.fields.get("PR", NONE) == NONE:
        return None, "no PR"
    if not command:
        return None, "no PR size command"
    try:
        result = run_command(command, journal, ctx, PR_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, "PR size command timed out"
    except (OSError, subprocess.SubprocessError):
        return None, "PR size command failed"
    if result.returncode != 0:
        return None, "PR size command failed"
    numbers = result.stdout.strip().split()
    if len(numbers) != 3 or not all(n.isdigit() for n in numbers):
        return None, "unexpected output"
    added, removed, files = (int(n) for n in numbers)
    return f"+{added} −{removed} · {quantity(files, 'file')}", None


def stats_lines(journal, tr, diff, read_at):
    """The body of `## Stats`, in its fixed, parseable format."""
    figs = journal_figures(journal)
    lines = []
    starts = [figs["created"]] if figs["created"] else []
    if tr.problem is None and tr.first:
        starts.append(tr.first.astimezone().replace(tzinfo=None))
    if starts:
        start = min(starts).replace(second=0, microsecond=0)
        end = (figs["closed"] or datetime.now()).replace(second=0, microsecond=0)
        lines.append(f"- **Elapsed**: {duration((end - start).total_seconds())} "
                     f"({start:%Y-%m-%d %H:%M} → {end:%Y-%m-%d %H:%M})")
    else:
        lines.append("- **Elapsed**: unavailable (no creation line)")
    corrected, stops = figs["stops"]
    blocking, other, logged = figs["findings"]
    stops_text = f"stops: {corrected} corrected of {stops}"
    findings = f"{logged} logged · {blocking} blocking, {other} other"
    if tr.problem:
        why = f"{tr.problem[0]} ({tr.problem[1]})"
        lines += [f"- **Agent time**: {why}",
                  f"- **User**: prompts {why} · {stops_text}",
                  f"- **Reviews**: runs {why}, {findings}",
                  f"- **Tokens**: {why}"]
    else:
        runs = tr.runs.get("jam:reviewer", 0)
        lines += [f"- **Agent time**: {duration(tr.agent_seconds)}",
                  f"- **User**: {quantity(tr.prompts, 'prompt')}, "
                  f"{quantity(tr.answers, 'answer')} · {stops_text}",
                  f"- **Reviews**: {quantity(runs, 'run')}, {findings}",
                  "- **Tokens** (out · in · cache write · cache read):"]
        groups = sorted(tr.tokens, key=lambda g: (g[0] != "main", g[0], g[1],
                                                  EFFORTS.index(g[2]) if g[2] in EFFORTS
                                                  else len(EFFORTS), g[2] or ""))
        for agent, model, effort in groups:
            label = agent if agent == "main" else f"{agent} ×{tr.runs.get(agent, 0)}"
            setting = f"{model} · {effort}" if effort else model
            values = " · ".join(token_count(n) for n in tr.tokens[(agent, model, effort)])
            lines.append(f"  - {label} · {setting}: {values}")
    text, reason = diff
    lines.append(f"- **Diff**: {text}" if text else f"- **Diff**: unavailable ({reason})")
    if tr.problem:
        lines.append(f"- **Context**: {tr.problem[0]} ({tr.problem[1]})")
    else:
        auto = f" ({tr.auto_compactions} automatic)" if tr.auto_compactions else ""
        lines.append(f"- **Context**: {quantity(tr.compactions, 'compaction')}{auto}, "
                     f"{quantity(tr.clears, 'clear')}")
    if tr.problem and tr.problem[0] == "unavailable":
        lines.append("- **Source**: none")
    else:
        # Kept when suspect: the version is what tells which update moved the format.
        versions = version_range(tr.versions)
        name = f"Claude Code {versions}" if versions else "Claude Code"
        lines.append(f"- **Source**: {name} transcripts, read {read_at} (local time)")
    return lines


def compute_stats(journal, ctx, bound):
    """(body of `## Stats`, transcripts, diff reason or None)."""
    worktree = journal.fields.get("Worktree", NONE)
    if worktree == NONE:
        tr = Transcripts(("unavailable", "no worktree"))
    else:
        try:
            tr = read_transcripts(worktree, bound)
        except Exception as exc:  # belt and braces: a close never fails on stats
            tr = Transcripts(("unavailable", f"unreadable transcripts: {one_line_error(exc)}"))
    try:
        diff = diff_figure(journal, ctx)
    except Exception as exc:
        diff = (None, f"PR size command failed: {one_line_error(exc)}")
    body = "\n".join(stats_lines(journal, tr, diff, now()))
    return body, tr, diff[1]


def stats_problem(tr):
    """The lesson about jam when the transcripts could not be trusted, else None.

    `no worktree` says nothing about jam; any other problem at close, `no transcript`
    included, means Claude Code's format or naming moved: the close itself runs in a
    session inside the worktree.
    """
    if not tr.problem or tr.problem == ("unavailable", "no worktree"):
        return None
    reason = f"{tr.problem[0]} ({' '.join(tr.problem[1].split())[:200]})"
    versions = version_range(tr.versions) or "version unknown"
    return f"jam: stats {reason} (Claude Code {versions})"


def cmd_stats(ctx, args):
    key = ctx.resolve_key(args.key)
    if ctx.journal(key).is_file():
        journal, bound = load(ctx.journal(key)), None
    elif ctx.archive(key).is_file():
        journal = load(ctx.archive(key))
        if journal.sections["Stats"]:
            # Transcripts get deleted after a while: the figures recorded at close last.
            sys.stdout.write(f"## Stats\n{journal.sections['Stats']}\n")
            return
        closed = journal_figures(journal)["closed"]
        bound = archive_bound(closed) if closed else None
    else:
        raise JamError(f"no journal at {ctx.journal(key)}")
    body = compute_stats(journal, ctx, bound)[0]
    sys.stdout.write(f"## Stats\n{body}\n")


# --- command line ------------------------------------------------------------

WRITES = {"init", "set", "stop", "close"}


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--key")
    common.add_argument("--cwd", default=".")
    parser = argparse.ArgumentParser(prog="journal.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("show", "next", "resume", "list", "stats"):
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
