"""Tests for skills/ticket/journal.py, numbered after docs/specs/journal.md."""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "ticket" / "journal.py"
sys.path.insert(0, str(SCRIPT.parent))

import journal  # noqa: E402

INIT_ARGS = ["--title", "Export", "--goal", "Download the orders as CSV",
             "--done-when", "- [ ] columns", "--resume", "Write the plan"]


# --- helpers -----------------------------------------------------------------

@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    """Isolate every test: its own JAM_HOME, no git config from the machine."""
    monkeypatch.setenv("JAM_HOME", str(tmp_path / "jamhome"))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))  # never the real one
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    for name in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{name}_NAME", "t")
        monkeypatch.setenv(f"GIT_{name}_EMAIL", "t@example.com")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def make_repo(path, branch=None, origin=None):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "commit", "-q", "--allow-empty", "-m", "init")
    if origin:
        git(path, "remote", "add", "origin", origin)
    if branch:
        git(path, "checkout", "-q", "-b", branch)
    return path


def run(capsys, cwd, *args):
    """Run the CLI in-process; return (exit code, stdout, stderr)."""
    try:
        code = journal.main([*args, "--cwd", str(cwd)])
    except SystemExit as exc:
        code = exc.code
    out, err = capsys.readouterr()
    return code, out, err


def fields(out):
    return dict(line.split("=", 1) for line in out.splitlines() if "=" in line)


def jam_home():
    return Path(os.environ["JAM_HOME"])


def write_project(path, **values):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Project", ""] + [f"- **{k}**: {v}" for k, v in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def personal_project(repo, **values):
    write_project(jam_home() / repo_id(repo) / "project.md", **values)


@pytest.fixture
def ticket(tmp_path, capsys):
    """A repository on branch 142-export with an initialized journal."""
    repo = make_repo(tmp_path / "shop", branch="142-export")
    code, _, err = run(capsys, repo, "init", *INIT_ARGS)
    assert code == 0, err
    return repo


def journal_path(capsys, repo, key=None):
    extra = ["--key", key] if key else []
    _, out, _ = run(capsys, repo, "key", *extra)
    return Path(fields(out)["journal"])


# --- key and repo-id ---------------------------------------------------------

def key_of(capsys, tmp_path, branch, pattern=None):
    repo = make_repo(tmp_path / branch.replace("/", "_"), branch=branch)
    if pattern:
        write_project(repo / ".jam" / "project.md", **{"Ticket pattern": pattern})
    code, out, err = run(capsys, repo, "key")
    assert code == 0, err
    return fields(out)["key"]


def test_01_declared_pattern(tmp_path, capsys):
    assert key_of(capsys, tmp_path, "abc-123-filter", r"ABC-\d+") == "ABC-123"
    assert key_of(capsys, tmp_path, "x/77-y", r"(\d+)-") == "77"
    # A group that does not take part in the match: the branch name, as with no match.
    assert key_of(capsys, tmp_path, "feat-x", r"ABC-(\d+)|feat") == "FEAT-X"


@pytest.mark.parametrize("branch, key", [
    ("142-export", "142"), ("feat/142-export", "142"),
    ("fix-2026-dates", "FIX-2026-DATES"), ("feat/abc-12-x", "FEAT-ABC-12-X"),
    ("refactor/auth", "REFACTOR-AUTH"),
])
def test_02_default_pattern(tmp_path, capsys, branch, key):
    assert key_of(capsys, tmp_path, branch) == key


def test_03_explicit_key(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="142-export")
    assert fields(run(capsys, repo, "key", "--key", "abc-12")[1])["key"] == "ABC-12"


def test_04_detached_head_and_outside_git(tmp_path, capsys):
    repo = make_repo(tmp_path / "r")
    git(repo, "checkout", "-q", "--detach")
    code, _, err = run(capsys, repo, "key")
    assert code == 1 and err
    outside = tmp_path / "plain"
    outside.mkdir()
    code, _, err = run(capsys, outside, "key")
    assert code == 1 and "git" in err


def repo_id(path):
    return journal.compute_repo_id(str(path))


def test_05_repo_id_from_origin(tmp_path):
    https = make_repo(tmp_path / "a", origin="https://github.com/acme/shop")
    ssh = make_repo(tmp_path / "b", origin="git@github.com:Acme/Shop.git")
    port = make_repo(tmp_path / "c",
                     origin="ssh://git@gitlab.example.com:2222/group/sub/app.git")
    local = make_repo(tmp_path / "d", origin="/srv/git/app.git")
    assert repo_id(https) == repo_id(ssh) == "acme-shop"
    assert repo_id(port) == "group-sub-app"
    assert repo_id(local) == "srv-git-app"
    git(https, "worktree", "add", "-q", "-b", "142-x", str(tmp_path / "wt"))
    assert repo_id(tmp_path / "wt") == "acme-shop"


def test_06_repo_id_without_origin(tmp_path):
    first = make_repo(tmp_path / "one" / "app")
    second = make_repo(tmp_path / "two" / "app")
    assert repo_id(first) != repo_id(second)
    assert repo_id(first).startswith("app-")
    git(first, "worktree", "add", "-q", "-b", "142-x", str(tmp_path / "wt"))
    assert repo_id(tmp_path / "wt") == repo_id(first)


def test_06b_keys_never_leave_jam_home(tmp_path, capsys):
    repo = make_repo(tmp_path / "r")
    git(repo, "checkout", "-q", "--detach")
    code, _, _ = run(capsys, repo, "key", "--key", "..")
    assert code == 1
    code, out, _ = run(capsys, repo, "key", "--key", ".x")
    assert code == 0
    path = Path(fields(out)["journal"]).resolve()
    assert path.name == "X.md" and jam_home().resolve() in path.parents


def test_07_same_key_two_repositories(tmp_path, capsys):
    one = make_repo(tmp_path / "one" / "app", branch="142-a")
    two = make_repo(tmp_path / "two" / "app", branch="142-b")
    assert journal_path(capsys, one) != journal_path(capsys, two)


# --- project files -----------------------------------------------------------

def test_08_personal_overrides_shared(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="abc-12-x")
    write_project(repo / ".jam" / "project.md", **{"Ticket pattern": r"nope-\d+"})
    personal_project(repo, **{"Ticket pattern": r"ABC-\d+"})
    out = run(capsys, repo, "key")[1]
    assert fields(out)["key"] == "ABC-12"
    assert len(fields(out)["project_files"].split(":")) == 2


def test_09_shared_stage_command_ignored(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="142-x")
    write_project(repo / ".jam" / "project.md", **{"Stage command": "touch marker"})
    code, _, err = run(capsys, repo, "init", *INIT_ARGS)
    assert code == 0
    assert "Stage command" in err
    assert not (repo / "marker").exists()


def test_09b_invalid_pattern(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="142-x")
    write_project(repo / ".jam" / "project.md", **{"Ticket pattern": "(oops"})
    code, _, err = run(capsys, repo, "key")
    assert code == 1 and "Ticket pattern" in err
    code, out, err = run(capsys, repo, "resume")
    assert (code, out, err) == (0, "", "")


def test_10_backticks_removed(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="abc-9-x")
    write_project(repo / ".jam" / "project.md", **{"Ticket pattern": r"`ABC-\d+`"})
    assert fields(run(capsys, repo, "key")[1])["key"] == "ABC-9"


# --- writing -----------------------------------------------------------------

def test_11_init_rules(tmp_path, capsys, ticket):
    text = journal_path(capsys, ticket).read_text(encoding="utf-8")
    assert "- **Size**: medium" in text and "- **Sensitive**: no" in text
    assert "- **Stage**: framing" in text and "created at framing" in text
    run(capsys, ticket, "set", "--decision", "keep me out")
    before = journal_path(capsys, ticket).read_bytes()
    code, _, err = run(capsys, ticket, "init", *INIT_ARGS)
    assert code == 1 and "nothing was written" in err
    assert journal_path(capsys, ticket).read_bytes() == before
    assert run(capsys, ticket, "init", *INIT_ARGS, "--force")[0] == 0
    assert "keep me out" not in journal_path(capsys, ticket).read_text("utf-8")
    archive = journal_path(capsys, ticket).parent.parent / "archive" / "142.md"
    archive.parent.mkdir()
    archive.write_text("old", encoding="utf-8")
    code, _, err = run(capsys, ticket, "init", *INIT_ARGS, "--force")
    assert code == 1 and str(archive) in err
    main = make_repo(tmp_path / "m")
    assert run(capsys, main, "init", *INIT_ARGS)[0] == 1
    trunk = make_repo(tmp_path / "t", origin="https://example.com/x/trunk.git")
    git(trunk, "branch", "-m", "trunk")
    git(trunk, "update-ref", "refs/remotes/origin/trunk", "HEAD")
    git(trunk, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    code, _, err = run(capsys, trunk, "init", *INIT_ARGS)
    assert code == 1 and "default branch" in err


def test_12_init_from_another_checkout(tmp_path, capsys):
    repo = make_repo(tmp_path / "r")
    assert run(capsys, repo, "init", "--key", "142", *INIT_ARGS)[0] == 0
    text = journal_path(capsys, repo, "142").read_text(encoding="utf-8")
    assert "- **Branch**: (none)" in text and "- **Worktree**: (none)" in text


@pytest.mark.parametrize("args, code", [
    (["--stage", "nope"], 2), (["--stage", "closed"], 2), (["--size", "huge"], 2),
    (["--sensitive", "maybe"], 2), ([], 1),
])
def test_13_refused_set_changes_nothing(capsys, ticket, args, code):
    before = journal_path(capsys, ticket).read_bytes()
    assert run(capsys, ticket, "set", *args)[0] == code
    assert journal_path(capsys, ticket).read_bytes() == before


def test_14_line_separators_are_normalized(capsys, ticket):
    assert run(capsys, ticket, "set", "--goal", "a\fb\u2028c\rd")[0] == 0
    path = journal_path(capsys, ticket)
    assert "## Goal\na\nb\nc\nd\n" in path.read_text(encoding="utf-8")
    assert run(capsys, ticket, "show")[1] == path.read_text(encoding="utf-8")


def test_14_one_line_and_multi_line_values(capsys, ticket):
    assert run(capsys, ticket, "set", "--decision", "keep\n  it   short")[0] == 0
    assert "- keep it short\n" in journal_path(capsys, ticket).read_text("utf-8")
    for option in ("--goal", "--plan", "--done-when", "--resume"):
        code, _, err = run(capsys, ticket, "set", option, "ok\n## Log\n- fake")
        assert code == 1 and "nothing was written" in err


def test_15_decision_imitating_a_stop(capsys, ticket):
    code, _, err = run(capsys, ticket, "set", "--decision", "Stop at framing: seen")
    assert code == 1 and "journal.py stop" in err
    assert run(capsys, ticket, "set", "--decision", "Stop the cron first")[0] == 0


def test_16_set_from_main_keeps_branch(tmp_path, capsys):
    main = make_repo(tmp_path / "main")
    worktree = tmp_path / "wt"
    git(main, "worktree", "add", "-q", "-b", "142-export", str(worktree))
    assert run(capsys, worktree, "init", *INIT_ARGS)[0] == 0
    assert run(capsys, main, "set", "--key", "142", "--plan", "1. do")[0] == 0
    text = journal_path(capsys, main, "142").read_text(encoding="utf-8")
    assert "- **Branch**: 142-export" in text
    assert f"- **Worktree**: {git(worktree, 'rev-parse', '--show-toplevel')}" in text


def log_lines(capsys, repo):
    text = journal_path(capsys, repo).read_text(encoding="utf-8")
    return text.split("## Log\n", 1)[1].strip().splitlines()


def test_17_log_lines(capsys, ticket):
    run(capsys, ticket, "set", "--stage", "code", "--decision", "a", "--decision", "b")
    assert log_lines(capsys, ticket)[-1].endswith(" · framing → code (+2 decisions)")
    run(capsys, ticket, "set", "--stage", "framing")
    run(capsys, ticket, "set", "--stage", "code", "--decision", "c")
    assert log_lines(capsys, ticket)[-1].endswith(" · framing → code (+1 decision)")
    run(capsys, ticket, "set", "--decision", "d", "--log", "tests green")
    assert log_lines(capsys, ticket)[-1].endswith(" · +1 decision · tests green")
    count = len(log_lines(capsys, ticket))
    run(capsys, ticket, "set", "--title", "New title")
    assert len(log_lines(capsys, ticket)) == count
    run(capsys, ticket, "set", "--stage", "code", "--log", "again")
    assert log_lines(capsys, ticket)[-1].endswith("· again")
    assert "→" not in log_lines(capsys, ticket)[-1]


def test_18_failed_write_keeps_journal(capsys, ticket, monkeypatch):
    path = journal_path(capsys, ticket)
    before = path.read_bytes()

    def broken(*_):
        raise OSError("disk full")

    monkeypatch.setattr(journal.os, "replace", broken)
    code, _, err = run(capsys, ticket, "set", "--plan", "1. other")
    assert code == 1 and "nothing was written" in err
    assert path.read_bytes() == before
    assert sorted(p.name for p in path.parent.iterdir()) == ["142.md"]


# --- stops, next, resume, list -----------------------------------------------

def test_19_stops(capsys, ticket):
    assert run(capsys, ticket, "stop", "corrected")[0] == 1
    assert run(capsys, ticket, "stop", "seen", "--about", "a (b)")[0] == 1
    assert run(capsys, ticket, "stop", "seen", "--about", "merge ok")[0] == 0
    text = journal_path(capsys, ticket).read_text(encoding="utf-8")
    assert "- Stop at framing (merge ok): seen\n" in text
    assert log_lines(capsys, ticket)[-1].endswith(" · stop at framing: seen")


def next_of(capsys, repo, stage, size="medium"):
    run(capsys, repo, "set", "--stage", stage, "--size", size)
    return fields(run(capsys, repo, "next")[1])


def test_20_next(capsys, ticket):
    assert next_of(capsys, ticket, "code") == {
        "current": "code", "next": "review", "clear_first": "yes"}
    assert next_of(capsys, ticket, "review")["clear_first"] == "yes"
    assert next_of(capsys, ticket, "acceptance")["clear_first"] == "no"
    assert next_of(capsys, ticket, "code", "small")["clear_first"] == "no"
    last = next_of(capsys, ticket, "follow-up")
    assert last["next"] == "closed" and "close" in last["hint"]


def test_21_resume(tmp_path, capsys, ticket):
    other = make_repo(tmp_path / "other", branch="7-x")
    assert run(capsys, other, "resume") == (0, "", "")
    run(capsys, ticket, "set", "--decision", "Semicolon separator")
    run(capsys, ticket, "stop", "seen")
    run(capsys, ticket, "stop", "corrected", "--note", "add the reason column")
    run(capsys, ticket, "set", "--resume", "\n".join(f"step {i}" for i in range(60)))
    code, out, _ = run(capsys, ticket, "resume")
    assert code == 0 and out.startswith("# 142 · Export")
    assert "Semicolon separator" in out and "add the reason column" in out
    assert "Stop at framing: seen" not in out
    assert len(out.splitlines()) <= 30 and "…" in out
    outside = tmp_path / "plain"
    outside.mkdir()
    assert run(capsys, outside, "resume") == (0, "", "")


def test_22_list_and_key(tmp_path, capsys, ticket):
    run(capsys, ticket, "init", "--key", "7", *INIT_ARGS)
    code, out, _ = run(capsys, ticket, "list")
    lines = out.splitlines()
    assert code == 0 and lines[0].split() == ["KEY", "STAGE", "PR", "UPDATED"]
    assert [line.split()[0] for line in lines[1:]] == ["142", "7"]
    assert len({line.index(line.split()[1]) for line in lines}) == 1
    empty = make_repo(tmp_path / "empty")
    assert run(capsys, empty, "list")[1].strip() == "no journal"
    git(empty, "checkout", "-q", "--detach")
    out = run(capsys, empty, "key", "--key", "9")[1]
    assert list(fields(out)) == ["key", "branch", "worktree", "main_worktree", "repo",
                                 "journal", "exists", "archived", "project_files",
                                 "reports"]
    assert fields(out)["branch"] == "" and fields(out)["project_files"] == ""


def test_22c_key_tells_the_main_worktree(tmp_path, capsys):
    # The ticket skill routes on it: start in the main worktree, framing in a linked one.
    main = make_repo(tmp_path / "main")
    git(main, "worktree", "add", "-q", "-b", "142-x", str(tmp_path / "wt"))
    assert fields(run(capsys, main, "key")[1])["main_worktree"] == "yes"
    assert fields(run(capsys, tmp_path / "wt", "key")[1])["main_worktree"] == "no"


def test_22b_key_for_another_branch_and_pattern(tmp_path, capsys):
    repo = make_repo(tmp_path / "r")
    code, out, _ = run(capsys, repo, "key", "--branch", "abc-7-x", "--pattern", r"ABC-\d+")
    assert code == 0 and fields(out)["key"] == "ABC-7"
    assert fields(out)["branch"] == "abc-7-x"
    assert not jam_home().exists()
    git(repo, "checkout", "-q", "--detach")
    assert fields(run(capsys, repo, "key", "--branch", "142-x")[1])["key"] == "142"
    code, _, err = run(capsys, repo, "key", "--branch", "x", "--pattern", "(oops")
    assert code == 1 and "pattern" in err
    # A broken pattern in the project file must not block proving its replacement.
    write_project(repo / ".jam" / "project.md", **{"Ticket pattern": "ABC-("})
    out = run(capsys, repo, "key", "--branch", "abc-9-x", "--pattern", r"ABC-\d+")[1]
    assert fields(out)["key"] == "ABC-9"


# --- commands and close ------------------------------------------------------

ENV_DUMP = ('printf "%s|" "$JAM_KEY" "$JAM_STAGE" "$JAM_REPO" "$JAM_PR" '
            '"$JAM_WORKTREE" "$JAM_RESUME" > "{out}"')


def test_23_stage_command(tmp_path, capsys, ticket, monkeypatch):
    out = tmp_path / "env.txt"
    personal_project(ticket, **{"Stage command": ENV_DUMP.format(out=out)})
    resume = "$(touch pwned)\nsecond line"
    assert run(capsys, ticket, "set", "--stage", "code", "--resume", resume)[0] == 0
    worktree = git(ticket, "rev-parse", "--show-toplevel")
    assert out.read_text().split("|")[:6] == [
        "142", "code", repo_id(ticket), "", worktree, "$(touch pwned)"]
    assert not (ticket / "pwned").exists()
    out.unlink()
    assert run(capsys, ticket, "set", "--stage", "nope")[0] == 2
    assert run(capsys, ticket, "set", "--decision", "Stop at code: seen")[0] == 1
    assert not out.exists()
    personal_project(ticket, **{"Stage command": "exit 3"})
    assert run(capsys, ticket, "set", "--stage", "review")[0] == 0
    personal_project(ticket, **{"Stage command": r"printf '\377'; printf '\377' >&2"})
    assert run(capsys, ticket, "set", "--stage", "acceptance")[0] == 0
    monkeypatch.setattr(journal, "STAGE_TIMEOUT", 0.3)
    personal_project(ticket, **{"Stage command": "sleep 5"})
    start = time.monotonic()
    assert run(capsys, ticket, "set", "--stage", "code")[0] == 0
    assert time.monotonic() - start < 2


def test_23_stage_command_needs_a_worktree(tmp_path, capsys):
    repo = make_repo(tmp_path / "r")
    personal_project(repo, **{"Stage command": f"touch {tmp_path / 'ran'}"})
    run(capsys, repo, "init", "--key", "5", *INIT_ARGS)
    run(capsys, repo, "set", "--key", "5", "--stage", "code")
    assert not (tmp_path / "ran").exists()


def test_24_close(tmp_path, capsys, ticket, monkeypatch):
    path = journal_path(capsys, ticket)
    archive = path.parent.parent / "archive" / "142.md"
    assert run(capsys, ticket, "close")[0] == 1
    run(capsys, ticket, "set", "--pr", "#12")
    assert run(capsys, ticket, "close")[0] == 1  # no PR state command
    before = path.read_bytes()
    monkeypatch.setattr(journal, "PR_TIMEOUT", 0.3)
    for command, reason in (("echo OPEN", "open"), ("exit 1", "failed"),
                            ("sleep 5", "timed out"), (r"printf '\377'", "not merged")):
        personal_project(ticket, **{"PR state command": command})
        start = time.monotonic()
        code, _, err = run(capsys, ticket, "close")
        assert time.monotonic() - start < 2
        assert code == 1 and reason in err and "nothing was written" in err
        assert path.read_bytes() == before
    personal_project(ticket, **{"PR state command": 'test "$JAM_PR" = "#12" && echo MERGED'})
    code, _, err = run(capsys, ticket, "close", "--pending", "tell the manager")
    assert code == 0, err
    assert not path.exists()
    text = archive.read_text(encoding="utf-8")
    assert "- **Stage**: closed" in text
    assert "Closed on " in text and "- tell the manager" in text
    assert log_lines_of(text)[-1].endswith(" · closed · 1 pending")
    path.write_text(text, encoding="utf-8")  # an active journal next to its archive
    code, _, err = run(capsys, ticket, "close", "--force")
    assert code == 1 and str(archive) in err
    assert path.read_text(encoding="utf-8") == text


def test_24b_close_gathers_jam_lessons(capsys, ticket):
    # Lessons about jam leave the project's journal for one file the maintainer reads.
    run(capsys, ticket, "set", "--lesson", "a trap in the code",
        "--lesson", "jam: the read command printed nothing", "--lesson", "JAM: two sessions",
        "--lesson", "jam: nothing to report")
    gathered = jam_home() / "jam-lessons.md"
    gathered.write_text("- an earlier line\n", encoding="utf-8")
    assert run(capsys, ticket, "close", "--force")[0] == 0
    lines = gathered.read_text(encoding="utf-8").splitlines()
    repo = fields(run(capsys, ticket, "key")[1])["repo"]
    assert lines[0] == "- an earlier line"
    lessons = [line for line in lines[1:] if "jam: stats" not in line]  # no transcript here
    assert [line.split(" · ", 1)[1] for line in lessons] == [
        f"{repo}#142 · jam: the read command printed nothing", f"{repo}#142 · JAM: two sessions"]
    assert all(line.startswith("- 20") for line in lessons)


def test_24b_close_survives_an_unwritable_lessons_file(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="9-x")
    run(capsys, repo, "init", *INIT_ARGS)
    run(capsys, repo, "set", "--lesson", "jam: something")
    (jam_home() / "jam-lessons.md").mkdir(parents=True)
    code, out, err = run(capsys, repo, "close", "--force")
    assert code == 0 and "archived=" in out and "not gathered" in err


def test_24_close_forced_without_pr(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="9-x")
    run(capsys, repo, "init", *INIT_ARGS)
    code, _, err = run(capsys, repo, "close", "--force")
    assert code == 0, err
    archive = journal_path(capsys, repo).parent.parent / "archive" / "9.md"
    assert log_lines_of(archive.read_text("utf-8"))[-1].endswith(
        " · closed (forced) · 0 pending")


def log_lines_of(text):
    return text.split("## Log\n", 1)[1].strip().splitlines()


def test_hook_runs_as_a_script(tmp_path, ticket):
    """The session-start hook calls the file directly: it must run standalone."""
    result = subprocess.run([sys.executable, str(SCRIPT), "resume"], cwd=ticket,
                            capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode == 0 and result.stdout.startswith("# 142 · Export")


def test_05_repo_id_of_bare_repository_from_its_worktree(tmp_path):
    bare = tmp_path / "code" / "app.git"
    bare.mkdir(parents=True)
    git(bare, "init", "-q", "--bare", "-b", "main")
    seed = make_repo(tmp_path / "seed")
    git(seed, "push", "-q", str(bare), "main")
    git(bare, "worktree", "add", "-q", "-b", "142-x", str(tmp_path / "wt"))
    assert repo_id(tmp_path / "wt").startswith("app.git-")


def test_24_close_checks_the_archive_first(capsys, ticket):
    path = journal_path(capsys, ticket)
    archive = path.parent.parent / "archive" / "142.md"
    archive.parent.mkdir()
    path.rename(archive)
    code, _, err = run(capsys, ticket, "close", "--force")
    assert code == 1 and str(archive) in err


def test_21_resume_is_silent_on_bad_arguments(capsys, ticket):
    for extra in (["--bogus"], ["-h"]):
        assert journal.main(["resume", *extra]) == 0
        assert capsys.readouterr() == ("", "")



# --- stats -------------------------------------------------------------------
# Fixture transcripts imitate what Claude Code writes under CLAUDE_CONFIG_DIR.

NO_PR = (None, "no PR")
T0 = datetime(2026, 11, 13, 10, 0, tzinfo=timezone.utc)
USAGE = {"output_tokens": 100, "input_tokens": 2, "cache_creation_input_tokens": 1000,
         "cache_read_input_tokens": 5000}


class Transcript:
    """Builds the entries of one transcript; times are seconds after T0."""

    def __init__(self, cwd, session="s1"):
        self.cwd, self.session, self.entries = str(cwd), session, []

    def add(self, t, kind, **extra):
        stamp = (T0 + timedelta(seconds=t)).isoformat().replace("+00:00", "Z")
        entry = {"type": kind, "timestamp": stamp, "cwd": self.cwd, "sessionId": self.session,
                 "uuid": f"{self.session}-{len(self.entries)}", "version": "2.1.296"}
        entry.update(extra)
        self.entries.append(entry)
        return self

    def prompt(self, t, text="do it", **extra):
        return self.add(t, "user", message={"role": "user", "content": text}, **extra)

    def assistant(self, t, mid=None, usage=None, tool=None, model="claude-opus-5-5",
                  effort="medium"):
        content = [{"type": "tool_use", "id": tool[0], "name": tool[1], "input": {}}] \
            if tool else [{"type": "text", "text": "ok"}]
        message = {"id": mid or f"m{len(self.entries)}", "model": model, "content": content,
                   "usage": dict(usage or USAGE)}
        extra = {"effort": effort} if effort else {}
        return self.add(t, "assistant", message=message, **extra)

    def result(self, t, tool_id="t1", **extra):
        block = {"type": "tool_result", "tool_use_id": tool_id, "content": "done"}
        return self.add(t, "user", message={"role": "user", "content": [block]}, **extra)

    def attachment(self, t, **attachment):
        return self.add(t, "attachment", attachment=attachment or {"type": "hook_success"})

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(e) + "\n" for e in self.entries),
                        encoding="utf-8")
        return path


@pytest.fixture
def claude():
    return Path(os.environ["CLAUDE_CONFIG_DIR"])


def project_dir(claude, worktree):
    name = re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(worktree))
    return claude / "projects" / name


def figures(worktree, bound=None):
    return journal.read_transcripts(str(worktree), bound)


def test_25_transcripts_found_from_the_worktree(tmp_path, claude):
    wt = make_repo(tmp_path / "wt")
    link = tmp_path / "link"
    link.symlink_to(wt)
    folder = project_dir(claude, wt)
    Transcript(link).prompt(0).assistant(60).write(folder / "a.jsonl")  # cwd through a symlink
    Transcript(tmp_path, "s2").prompt(0).assistant(60).write(folder / "b.jsonl")  # elsewhere
    moved = Transcript(wt, "s3").prompt(0).assistant(60)
    moved.cwd = str(tmp_path / "scratch")
    moved.prompt(120).assistant(180)  # moved out: still the ticket's session
    moved.write(folder / "c.jsonl")
    tr = figures(link)
    assert tr.problem is None and tr.prompts == 3
    # Entries after the bound are not counted.
    assert figures(wt, T0 + timedelta(seconds=90)).prompts == 2


@pytest.fixture
def paris(monkeypatch):
    """Run in a known time zone, then give the machine's back."""
    if not hasattr(time, "tzset"):
        pytest.skip("time zones cannot be switched on this platform")
    monkeypatch.setenv("TZ", "Europe/Paris")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


def test_25_archive_bound_is_local_time_start_of_minute(paris):
    bound = journal.archive_bound(datetime(2026, 11, 13, 22, 1))
    assert bound == datetime(2026, 11, 13, 21, 1, tzinfo=timezone.utc)


def test_26_agent_time(tmp_path, claude):
    wt = make_repo(tmp_path / "wt")
    folder = project_dir(claude, wt)
    (Transcript(wt)
     .prompt(0)                                   # the user asks
     .assistant(10, tool=("t1", "Bash"))          # busy 0 → 10
     .attachment(69.997)                          # hook stamped before the result
     .result(70, "t1")                            # busy 10 → 70, the tool ran
     .assistant(80)                               # busy 70 → 80
     .prompt(3600)                                # a wait: not counted
     .assistant(3610, tool=("q1", "AskUserQuestion"))   # busy 10 s
     .result(5000, "q1")                          # an answer: a wait
     .assistant(5010, tool=("t2", "Bash"))        # busy 10 s
     .result(6000, "t2", permissionDecision={"source": "user_temporary"})  # permission: wait
     .assistant(6010)                             # busy 10 s
     .add(9000, "user", isMeta=True, message={"role": "user",
                                               "content": "Another Claude session sent"})
     .assistant(9010)                             # busy 10 s after a message: not 3000 s
     .prompt(9500, "<task-notification>done</task-notification>")
     .assistant(9520)                             # busy 20 s
     .write(folder / "a.jsonl"))
    tr = figures(wt)
    assert tr.agent_seconds == pytest.approx(80 + 10 + 10 + 10 + 10 + 20)
    # A background subagent overlapping the main session is counted once.
    sub = Transcript(wt, "sub").prompt(5, "review this").assistant(50).assistant(200)
    sub.write(folder / "a" / "subagents" / "agent-x.jsonl")
    tr = figures(wt)
    # Busy 5 → 200 overlaps 0 → 80: the union adds 80 → 200.
    assert tr.agent_seconds == pytest.approx(200 + 10 + 10 + 10 + 10 + 20)


def test_27_tokens(tmp_path, claude):
    wt = make_repo(tmp_path / "wt")
    folder = project_dir(claude, wt)
    session = Transcript(wt).prompt(0)
    for output in (2, 2, 1604, None):  # one message over lines, partial counts first
        session.assistant(10, mid="msg1", usage=dict(USAGE, output_tokens=output))
    session.assistant(15, mid="msg2", effort="high")  # /effort changed mid-session
    session.assistant(20, mid="syn", model="<synthetic>")
    session.write(folder / "a.jsonl")
    session.write(folder / "fork.jsonl")  # a forked copy: same messages, same uuids
    sub = Transcript(wt, "r").prompt(1, "review").assistant(5, mid="r1", effort="xhigh")
    sub.write(folder / "a" / "subagents" / "agent-r.jsonl")
    (folder / "a" / "subagents" / "agent-r.meta.json").write_text(
        '{"agentType": "jam:reviewer"}', encoding="utf-8")
    Transcript(wt, "u").prompt(1, "x").assistant(5, mid="u1", effort=None).write(
        folder / "a" / "subagents" / "agent-u.jsonl")  # no meta: unknown
    Transcript(wt, "l").prompt(99999, "late").write(
        folder / "a" / "subagents" / "agent-late.jsonl")
    tr = figures(wt, T0 + timedelta(seconds=600))
    assert tr.tokens[("main", "claude-opus-5-5", "medium")] == [1604, 2, 1000, 5000]
    assert all(g[1] != "<synthetic>" for g in tr.tokens) and tr.problem is None
    assert tr.runs == {"jam:reviewer": 1, "unknown": 1}  # the late one never ran in time
    assert tr.prompts == 1  # the fork counts once, subagent requests never
    lines = journal.stats_lines(journal.Journal.parse(JOURNAL_TEXT), tr, NO_PR, "now")
    assert lines.index("  - main · claude-opus-5-5 · medium: 1.6k · 2 · 1.0k · 5.0k") \
        < lines.index("  - main · claude-opus-5-5 · high: 100 · 2 · 1.0k · 5.0k")
    assert "  - jam:reviewer ×1 · claude-opus-5-5 · xhigh: 100 · 2 · 1.0k · 5.0k" in lines
    assert "  - unknown ×1 · claude-opus-5-5: 100 · 2 · 1.0k · 5.0k" in lines


def test_28_prompts_and_answers(tmp_path, claude):
    wt = make_repo(tmp_path / "wt")
    folder = project_dir(claude, wt)
    image = [{"type": "image", "source": {}}]
    (Transcript(wt)
     .prompt(0, "typed")
     .prompt(1, image)
     .attachment(2, type="queued_command", origin={"kind": "human"}, prompt="also this")
     .prompt(3, "meta", isMeta=True)
     .prompt(4, "summary", isCompactSummary=True)
     .prompt(5, "from the system", promptSource="system")
     .prompt(6, "<task-notification>x</task-notification>")
     .prompt(7, "<command-name>/clear</command-name>")
     .prompt(8, "<bash-stdout>ok</bash-stdout>")
     .prompt(8.5, "[Request interrupted by user for tool use]")
     .prompt(8.6, [{"type": "text", "text": None}, {"type": "text", "text": "null skipped"}])
     .assistant(9, tool=("q", "AskUserQuestion"))
     .result(10, "q")
     .assistant(11, tool=("b", "Bash"))
     .result(12, "b", toolUseResult="User rejected tool use")
     .write(folder / "a.jsonl"))
    Transcript(wt, "s9").prompt(0, "Name this chat").add(1, "assistant", entrypoint="sdk-cli",
                                                          message={}).write(folder / "t.jsonl")
    tr = figures(wt)
    assert (tr.prompts, tr.answers, tr.clears) == (4, 2, 1)


def test_29_unreadable_and_unavailable(tmp_path, claude):
    wt = make_repo(tmp_path / "wt")
    assert figures(wt).problem == ("unavailable", "no transcript")
    folder = project_dir(claude, wt)
    Transcript(tmp_path / "x", "t").prompt(0).write(folder / "t.jsonl")
    assert figures(wt).problem == ("unavailable", "no session in the worktree")
    path = Transcript(wt).prompt(0).assistant(10).write(folder / "a.jsonl")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write('{"type": "user", "cwd": "x"}\n{"truncated\n')
    tr = figures(wt)
    assert tr.problem is None and tr.prompts == 1
    # Entries but no usage: suspect. An empty session next to a normal one is not.
    Transcript(wt, "e").attachment(0).write(folder / "empty.jsonl")
    assert figures(wt).problem is None
    no_usage = Transcript(wt, "n").prompt(0)
    no_usage.add(5, "assistant", message={"id": "z", "content": []})
    path.unlink()
    no_usage.write(folder / "a.jsonl")
    assert figures(wt).problem == ("suspect", "no usage")


def test_29_reader_never_raises(tmp_path, claude, monkeypatch):
    wt = make_repo(tmp_path / "wt")
    Transcript(wt).prompt(0).assistant(5).write(project_dir(claude, wt) / "a.jsonl")

    def broken(*args):
        raise ValueError("line one\nline two " + "x" * 300)

    monkeypatch.setattr(journal, "classify", broken)
    status, reason = figures(wt).problem
    assert status == "unavailable" and reason.startswith("unreadable transcripts")
    assert "\n" not in reason and len(reason) < 200
    line = journal.stats_problem(figures(wt))
    assert line.endswith(") (Claude Code version unknown)")


JOURNAL_TEXT = """# 142 · Export

- **Stage**: follow-up
- **Size**: medium
- **Sensitive**: no
- **Branch**: 142-export
- **Worktree**: (none)
- **PR**: 7
- **Updated**: 2026-11-13 22:01

## Goal
g

## Done when
d

## Plan

## Decisions
- Stop at framing: corrected, shorter
- Stop at acceptance (merge): seen

## Resume here
r

## Lessons

## Log
- 2026-11-13 15:35 · created at framing
- 2026-11-13 16:06 · review: 1 blocking (CSRF #306 (fix f(x)) done), 6 other (see #12)
- 2026-11-13 16:10 · review → acceptance · review: 0 blocking, 2 other, applied
- 2026-11-13 16:11 · review ciblée: 0 blocking
- 2026-11-13 22:01 · closed · 0 pending
"""


def test_30_journal_figures():
    twice = JOURNAL_TEXT + "- 2026-11-14 09:00 · closed (forced) · 0 pending\n"
    assert journal.journal_figures(journal.Journal.parse(twice))["closed"] == datetime(
        2026, 11, 14, 9, 0)  # the last close counts
    figs = journal.journal_figures(journal.Journal.parse(JOURNAL_TEXT))
    assert figs["stops"] == (1, 2)
    assert figs["findings"] == (1, 8, 2)
    assert figs["created"] == datetime(2026, 11, 13, 15, 35)
    assert figs["closed"] == datetime(2026, 11, 13, 22, 1)


@pytest.mark.parametrize("seconds, text", [
    (0, "0 min"), (89, "1 min"), (90, "2 min"), (3599, "1 h 00"), (3600, "1 h 00"),
    (23_460, "6 h 31"), (90_000, "1 d 1 h")])
def test_30_durations(seconds, text):
    assert journal.duration(seconds) == text


@pytest.mark.parametrize("count, text", [
    (198, "198"), (1_000, "1.0k"), (33_443, "33.4k"), (99_960, "100k"),
    (218_813, "219k"), (999_600, "1.0M"), (8_649_345, "8.6M")])
def test_30_token_counts(count, text):
    assert journal.token_count(count) == text


def test_30_elapsed_and_versions():
    j = journal.Journal.parse(JOURNAL_TEXT)
    tr = journal.Transcripts()
    tr.first = datetime(2026, 11, 13, 15, 29, 36).astimezone(timezone.utc)
    tr.versions = {"2.1.10", "2.1.9"}
    lines = journal.stats_lines(j, tr, ("+62 −1 · 3 files", None), "2026-11-13 22:01")
    assert lines[0] == "- **Elapsed**: 6 h 32 (2026-11-13 15:29 → 2026-11-13 22:01)"
    assert lines[-1] == ("- **Source**: Claude Code 2.1.9–2.1.10 transcripts, "
                         "read 2026-11-13 22:01 (local time)")
    no = journal.Transcripts(problem=("unavailable", "no transcript"))
    lines = journal.stats_lines(j, no, (None, "no PR size command"), "x")
    assert lines == [
        "- **Elapsed**: 6 h 26 (2026-11-13 15:35 → 2026-11-13 22:01)",
        "- **Agent time**: unavailable (no transcript)",
        "- **User**: prompts unavailable (no transcript) · stops: 1 corrected of 2",
        "- **Reviews**: runs unavailable (no transcript), 2 logged · 1 blocking, 8 other",
        "- **Tokens**: unavailable (no transcript)",
        "- **Diff**: unavailable (no PR size command)",
        "- **Context**: unavailable (no transcript)",
        "- **Source**: none"]
    bare = journal.Journal.parse(JOURNAL_TEXT.replace(
        "- 2026-11-13 15:35 · created at framing\n", ""))
    assert journal.stats_lines(bare, no, NO_PR, "x")[0] == (
        "- **Elapsed**: unavailable (no creation line)")


def test_30b_diff(tmp_path, capsys, ticket, monkeypatch):
    j = journal.load(journal_path(capsys, ticket))
    ctx = journal.Context(str(ticket))
    assert journal.diff_figure(j, ctx) == (None, "no PR")
    j.fields["PR"] = "7"
    assert journal.diff_figure(j, ctx) == (None, "no PR size command")
    for command, expected in [
            ('printf "62 1 3\\n"', ("+62 −1 · 3 files", None)),
            ('echo "$JAM_PR 0 1"', ("+7 −0 · 1 file", None)),
            ("echo 62 1", (None, "unexpected output")),
            ("exit 3", (None, "PR size command failed"))]:
        ctx.project["PR size command"] = command
        assert journal.diff_figure(j, ctx) == expected
    ctx.project["PR size command"] = "sleep 5"
    monkeypatch.setattr(journal, "PR_TIMEOUT", 0.2)
    assert journal.diff_figure(j, ctx) == (None, "PR size command timed out")


def test_30b_context(tmp_path, claude):
    wt = make_repo(tmp_path / "wt")
    folder = project_dir(claude, wt)
    session = (Transcript(wt).prompt(0).assistant(5)
               .add(6, "system", subtype="compact_boundary", compactMetadata={"trigger": "auto"})
               .add(7, "system", subtype="compact_boundary",
                    compactMetadata={"trigger": "manual"})
               .assistant(8))
    session.write(folder / "a.jsonl")
    session.write(folder / "fork.jsonl")
    Transcript(wt, "c").prompt(0, "<command-name>/clear</command-name>").assistant(3).write(
        folder / "b.jsonl")
    tr = figures(wt)
    assert (tr.compactions, tr.auto_compactions, tr.clears) == (2, 1, 1)
    lines = journal.stats_lines(journal.Journal.parse(JOURNAL_TEXT), tr, NO_PR, "x")
    assert "- **Context**: 2 compactions (1 automatic), 1 clear" in lines
    tr.compactions, tr.auto_compactions = 1, 0
    assert "- **Context**: 1 compaction, 1 clear" in journal.stats_lines(
        journal.Journal.parse(JOURNAL_TEXT), tr, NO_PR, "x")


def test_31_close_writes_stats(tmp_path, capsys, ticket, claude):
    Transcript(ticket).prompt(0).assistant(60).write(project_dir(claude, ticket) / "a.jsonl")
    personal_project(ticket, **{"PR size command": "`echo 5 2 1`"})
    run(capsys, ticket, "set", "--pr", "9", "--lesson", "a lesson")
    code, _, err = run(capsys, ticket, "close", "--force")
    assert code == 0, err
    archive = journal_path(capsys, ticket).parent.parent / "archive" / "142.md"
    text = archive.read_text(encoding="utf-8")
    assert text.index("## Lessons") < text.index("## Stats") < text.index("## Log")
    assert "- **Agent time**: 1 min" in text and "- **Diff**: +5 −2 · 1 file" in text
    stats = text.split("## Stats\n", 1)[1].split("\n\n## Log", 1)[0]
    # stats on an archive prints the recorded section unchanged.
    code, out, _ = run(capsys, ticket, "stats")
    assert code == 0 and out == f"## Stats\n{stats}\n"
    assert not (jam_home() / "jam-lessons.md").exists()  # nothing to report


def test_31_close_survives_a_broken_reader(capsys, ticket, monkeypatch):
    monkeypatch.setattr(journal, "read_transcripts", lambda *a: 1 / 0)
    code, out, err = run(capsys, ticket, "close", "--force")
    assert code == 0 and "archived=" in out
    text = (journal_path(capsys, ticket).parent.parent / "archive" / "142.md").read_text("utf-8")
    assert "- **Agent time**: unavailable (" in text and "- **Elapsed**: " in text


def test_29_close_reports_transcript_problems(capsys, ticket):
    # No transcript although the close runs in the worktree: reported, once.
    code, _, err = run(capsys, ticket, "close", "--force")
    assert code == 0
    assert "jam: stats unavailable (no transcript) (Claude Code version unknown)\n" in err
    assert "jam: jam:" not in err
    lines = (jam_home() / "jam-lessons.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert lines[0].endswith("#142 · jam: stats unavailable (no transcript) "
                             "(Claude Code version unknown)")


def test_29_close_without_worktree_reports_nothing(tmp_path, capsys):
    repo = make_repo(tmp_path / "r")
    run(capsys, repo, "init", "--key", "9", *INIT_ARGS)
    code, _, err = run(capsys, repo, "close", "--key", "9", "--force")
    assert code == 0 and "stats" not in err
    assert not (jam_home() / "jam-lessons.md").exists()


def test_30b_close_reports_a_failing_size_command(tmp_path, capsys, ticket, claude):
    Transcript(ticket).prompt(0).assistant(60).write(project_dir(claude, ticket) / "a.jsonl")
    personal_project(ticket, **{"PR size command": "exit 1"})
    run(capsys, ticket, "set", "--pr", "9")
    code, out, err = run(capsys, ticket, "close", "--force")
    assert code == 0 and "archived=" in out and "PR size command failed" in err
    assert not (jam_home() / "jam-lessons.md").exists()


def test_31_stats_on_an_active_journal(tmp_path, capsys, ticket, claude):
    Transcript(ticket).prompt(0).assistant(60).write(project_dir(claude, ticket) / "a.jsonl")
    code, out, _ = run(capsys, ticket, "stats")
    assert code == 0 and out.startswith("## Stats\n- **Elapsed**: ")
    assert "- **User**: 1 prompt, 0 answers · stops: 0 corrected of 0" in out
    # An active journal is never rendered with an empty Stats section.
    assert "## Stats" not in journal_path(capsys, ticket).read_text(encoding="utf-8")


def test_31_stats_without_journal(tmp_path, capsys):
    repo = make_repo(tmp_path / "r", branch="5-x")
    code, _, err = run(capsys, repo, "stats")
    assert code == 1 and "no journal" in err


def lessons_file_lines():
    path = jam_home() / "jam-lessons.md"
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def test_29_close_reports_a_suspect_reading(capsys, ticket, claude):
    session = Transcript(ticket).prompt(0)
    session.add(5, "assistant", message={"id": "z", "content": []})  # usage gone
    session.write(project_dir(claude, ticket) / "a.jsonl")
    code, _, err = run(capsys, ticket, "close", "--force")
    assert code == 0 and "jam: stats suspect (no usage) (Claude Code 2.1.296)\n" in err
    assert lessons_file_lines()[0].endswith(
        "#142 · jam: stats suspect (no usage) (Claude Code 2.1.296)")
    archive = journal_path(capsys, ticket).parent.parent / "archive" / "142.md"
    assert "- **Source**: Claude Code 2.1.296 transcripts" in archive.read_text("utf-8")


def test_29_only_a_chat_namer_session(capsys, ticket, claude):
    namer = Transcript(ticket, "n").prompt(0, "Name this chat")
    namer.add(1, "assistant", entrypoint="sdk-cli", message={})
    namer.write(project_dir(claude, ticket) / "n.jsonl")
    assert figures(ticket).problem == ("unavailable", "no session in the worktree")
    code, _, err = run(capsys, ticket, "close", "--force")
    assert code == 0 and "jam: stats unavailable (no session in the worktree)" in err
    assert len(lessons_file_lines()) == 1


def test_31_second_close_after_a_failed_move(capsys, ticket, monkeypatch):
    personal_project(ticket, **{"PR size command": "echo 5 2 1"})
    run(capsys, ticket, "set", "--pr", "9")
    real_replace = journal.os.replace
    failures = []

    def replace(src, dst):
        if "archive" in str(dst) and not failures:
            failures.append(dst)
            raise OSError("disk full")
        real_replace(src, dst)

    monkeypatch.setattr(journal.os, "replace", replace)
    assert run(capsys, ticket, "close", "--force")[0] == 1
    path = journal_path(capsys, ticket)
    active = path.read_text(encoding="utf-8")
    # The active journal left at `closed` carries its stats; show and resume read it.
    assert "## Stats" in active and run(capsys, ticket, "show")[1] == active
    assert run(capsys, ticket, "resume")[1].startswith("# 142 · Export")
    assert journal.load(path).sections["Lessons"] == ""
    assert lessons_file_lines() == []  # written only once the archive exists
    personal_project(ticket, **{"PR size command": "echo 6 2 1"})
    assert run(capsys, ticket, "close", "--force")[0] == 0
    text = (path.parent.parent / "archive" / "142.md").read_text(encoding="utf-8")
    # The second close replaced the section: new figures, once.
    assert "- **Diff**: +6 −2 · 1 file" in text and "+5 −2" not in text
    assert text.count("- **Elapsed**") == 1
    assert len([line for line in log_lines_of(text) if " · closed" in line]) == 2
    assert len(lessons_file_lines()) == 1


def test_31_stats_prints_the_recorded_section(capsys, ticket, claude):
    folder = project_dir(claude, ticket)
    Transcript(ticket).prompt(0).assistant(60).write(folder / "a.jsonl")
    personal_project(ticket, **{"PR size command": "echo 5 2 1"})
    run(capsys, ticket, "set", "--pr", "9")
    assert run(capsys, ticket, "close", "--force")[0] == 0
    recorded = run(capsys, ticket, "stats")[1]
    # Recomputing would now give other figures: the recorded ones must come back.
    (folder / "a.jsonl").unlink()
    personal_project(ticket, **{"PR size command": "echo 50 20 10"})
    assert run(capsys, ticket, "stats")[1] == recorded
    assert "- **Diff**: +5 −2 · 1 file" in recorded


def test_31_stats_on_an_archive_without_section(capsys, ticket, claude, paris):
    # Journals archived before stats existed: computed, bounded by the close's minute.
    closed = (T0 + timedelta(minutes=30)).astimezone().strftime("%Y-%m-%d %H:%M")
    text = JOURNAL_TEXT.replace("- **Worktree**: (none)", f"- **Worktree**: {ticket}")
    text = text.replace("2026-11-13 22:01 · closed", f"{closed} · closed")
    archive = journal_path(capsys, ticket).parent.parent / "archive" / "142.md"
    archive.parent.mkdir(parents=True)
    archive.write_text(text, encoding="utf-8")
    journal_path(capsys, ticket).unlink()
    (Transcript(ticket).prompt(0).assistant(60)
     .prompt(40 * 60, "after the close").assistant(40 * 60 + 5)
     .write(project_dir(claude, ticket) / "a.jsonl"))
    code, out, err = run(capsys, ticket, "stats")
    assert code == 0, err
    assert "- **User**: 1 prompt, 0 answers" in out and "- **Agent time**: 1 min" in out
    assert archive.read_text(encoding="utf-8") == text  # read-only
