"""Tests for skills/ticket/journal.py, numbered after docs/specs/journal.md."""

import os
import subprocess
import sys
import time
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
    run(capsys, ticket, "stop", "corrected", "--note", "add the level column")
    run(capsys, ticket, "set", "--resume", "\n".join(f"step {i}" for i in range(60)))
    code, out, _ = run(capsys, ticket, "resume")
    assert code == 0 and out.startswith("# 142 · Export")
    assert "Semicolon separator" in out and "add the level column" in out
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
    assert list(fields(out)) == ["key", "branch", "worktree", "repo", "journal",
                                 "exists", "archived", "project_files", "reports"]
    assert fields(out)["branch"] == "" and fields(out)["project_files"] == ""


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
