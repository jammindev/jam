#!/usr/bin/env python3
"""Tests for maintainer_time.py — the maintainer's time on a task, from transcripts.

Each case writes synthetic Claude Code transcripts (one JSONL file per session,
under projects/<folder>/, as Claude Code lays them out) in a temp folder, runs
the script as the recetteur would, and reads its report on stdout. The events
carry the fields the script reads: type, timestamp, cwd, sessionId,
isSidechain and message.content (text, tool_use, tool_result blocks).

Run: python3 -m unittest scripts.test_maintainer_time
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "maintainer_time.py")

MAIN = "/work/projet"
TASK = "/work/projet-worktrees/23-tache"
ISSUE = "23"
DAY = "2026-10-12T"
# Never printed: the report holds counts and times, no message content.
WITNESS = "ZORGLUB"


def at(clock):
    return f"{DAY}{clock}:00.000Z"


def user(clock, text, **extra):
    return dict(type="user", timestamp=at(clock),
                message={"role": "user", "content": text}, **extra)


def assistant(clock, text=None):
    """An answer of the agent: some text, or a tool call alone."""
    if text:
        blocks = [{"type": "text", "text": text}]
    else:
        blocks = [{"type": "tool_use", "name": "Bash", "id": "tu-1",
                   "input": {"command": "git status"}}]
    return dict(type="assistant", timestamp=at(clock),
                message={"role": "assistant", "content": blocks})


class MaintainerTimeTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="maintainer-time-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.projects = os.path.join(self.root, "config", "projects")

    def session(self, cwd, name, *events):
        """Write one session's transcript: every event gets its cwd and id."""
        folder = os.path.join(self.projects, cwd.replace("/", "-"))
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, name + ".jsonl"), "w", encoding="utf-8") as fh:
            for event in events:
                row = dict(cwd=cwd, sessionId=name, isSidechain=False)
                row.update(event)
                fh.write(json.dumps(row) + "\n")

    def run_script(self, *extra, transcripts=True, env=None, main=MAIN, worktree=TASK, cwd=None):
        args = [sys.executable, SCRIPT, "--main", main, "--worktree", worktree,
                "--issue", ISSUE, *extra]
        if transcripts:
            args += ["--transcripts", self.projects]
        if env is None:
            env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
            env["HOME"] = os.path.join(self.root, "empty-home")
        done = subprocess.run(args, capture_output=True, text=True, env=env, timeout=30,
                              cwd=cwd)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn(WITNESS, done.stdout + done.stderr)
        return done.stdout

    def assertTotal(self, out, minutes, moments, messages):
        self.assertIn(f"[jam] Temps du mainteneur : {minutes} min en {moments} moment(s), "
                      f"{messages} message(s) retenu(s)\n", out)

    # --- moments and margin ------------------------------------------------

    def test_moments_and_margin(self):
        # Under 10 min apart: one moment, (last - first) + 3 min of reading.
        # Exactly 10 min apart: a new moment.
        self.session(MAIN, "s1",
                     user("10:05", "question #23 " + WITNESS),
                     user("10:12", "ok #23 " + WITNESS),
                     user("10:22", "encore #23 " + WITNESS),
                     user("11:00", "fin #23 " + WITNESS))
        out = self.run_script()
        # 10:05-10:12 -> 10 min ; 10:22 -> 3 ; 11:00 -> 3.
        self.assertTotal(out, 16, 3, 4)
        self.assertIn("- 2026-10-12 10:05Z → 10:12Z : 10 min\n", out)
        self.assertIn("- 2026-10-12 10:22Z → 10:22Z : 3 min\n", out)
        # The figure goes into the PR as is: what it leaves out must travel with it.
        self.assertIn("\nNon comptés : recette du mainteneur et feux verts tapés "
                      "dans le worktree de la tâche", out)

    def test_nothing_found(self):
        os.makedirs(self.projects)
        out = self.run_script()
        self.assertTotal(out, 0, 0, 0)
        # A zero must show where it comes from: no session at all.
        self.assertIn("0 session(s) du worktree principal lue(s)\n", out)

    def test_relative_main_path(self):
        # Run from the main worktree with --main as typed: the path is made
        # absolute, as the transcripts' cwd is.
        main = os.path.join(self.root, "projet")
        os.makedirs(main)
        self.session(main, "s1", user("10:00", "on lance #23"), user("10:05", "ok #23"))
        out = self.run_script(main=".", cwd=main)
        self.assertTotal(out, 8, 1, 2)
        self.assertIn("1 session(s) du worktree principal lue(s)\n", out)

    def test_main_path_through_a_symbolic_link(self):
        # A path through a link and the physical path name the same worktree,
        # whichever side the link is on.
        main = os.path.join(self.root, "projet")
        link = os.path.join(self.root, "lien")
        os.makedirs(main)
        os.symlink(main, link)
        for label, recorded, given in (("given by the link", main, link),
                                       ("recorded by the link", link, main)):
            with self.subTest(case=label):
                shutil.rmtree(self.projects, ignore_errors=True)
                self.session(recorded, "s1", user("10:00", "ok #23"))
                out = self.run_script(main=given)
                self.assertIn("1 session(s) du worktree principal lue(s)\n", out)

    def test_missing_folder_is_an_error(self):
        # A wrong path must not read as "0 min": that would be a false measure.
        done = subprocess.run([sys.executable, SCRIPT, "--main", MAIN, "--worktree", TASK,
                               "--transcripts", os.path.join(self.root, "nulle-part")],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
        self.assertEqual(done.stdout, "")

    # --- what is not the maintainer talking --------------------------------

    def test_injected_messages_left_out(self):
        tool_result = {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tu-1", "content": "ok " + WITNESS}]}
        self.session(MAIN, "s1",
                     user("10:01", "ok #23 " + WITNESS, isMeta=True),
                     dict(type="user", timestamp=at("10:02"), message=tool_result),
                     user("10:03", "<task-notification>fini #23</task-notification>"),
                     user("10:04", "<bash-input>git status #23</bash-input>"),
                     user("10:05", "<bash-stdout>rien #23 " + WITNESS + "</bash-stdout>"),
                     user("10:06", "résumé #23 " + WITNESS, isCompactSummary=True),
                     user("10:07", "ok sous-agent #23 " + WITNESS, isSidechain=True),
                     user("10:40", "le seul vrai message #23 " + WITNESS))
        out = self.run_script()
        self.assertTotal(out, 3, 1, 1)

    def test_task_worktree_sessions_not_read(self):
        # Everything typed in a session of the task's worktree comes from an
        # agent: briefs, relays sent through a shell variable, pasted blocks.
        # Only the coordinator's sessions are read.
        self.session(TASK, "orch",
                     user("10:00", "brief #23 " + WITNESS),
                     user("10:30", "feu vert plan de #23, « ok » " + WITNESS))
        self.session(TASK, "role", user("11:00", "brief 23-tache " + WITNESS))
        self.session(MAIN, "coord", user("12:00", "on lance #23"))
        out = self.run_script()
        self.assertTotal(out, 3, 1, 1)
        self.assertIn("1 session(s) du worktree principal lue(s)\n", out)
        self.assertIn("Écartés : 0 hors tâche, 0 hors fenêtre", out)

    def test_other_sessions_not_read_past_their_first_cwd(self):
        # A transcript is kept or dropped on its first cwd: the rest of a
        # foreign file is never loaded, whatever it holds.
        self.session("/work/ailleurs", "free",
                     user("10:00", "rien"),
                     user("10:40", "ok #23 " + WITNESS, cwd=MAIN, sessionId="glisse"))
        out = self.run_script()
        self.assertTotal(out, 0, 0, 0)

    def test_unreadable_transcript_skipped(self):
        # The transcripts folder of a real machine holds broken symbolic links
        # (a sub-agent's transcript pointing to a folder since removed): such
        # a file is skipped, the others are still read.
        self.session(MAIN, "coord", user("10:00", "ok #23"))
        os.symlink(os.path.join(self.root, "disparu", "x.jsonl"),
                   os.path.join(self.projects, "lien-casse.jsonl"))
        out = self.run_script()
        self.assertTotal(out, 3, 1, 1)
        self.assertIn("1 session(s) du worktree principal lue(s)\n", out)

    def test_transcript_without_cwd_not_read(self):
        # A session that cannot be placed is not the coordinator's: with a
        # mistyped --main, it would otherwise turn a zero into a measure.
        folder = os.path.join(self.projects, "x")
        os.makedirs(folder)
        with open(os.path.join(folder, "sans-cwd.jsonl"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "summary", "summary": "résumé"}) + "\n")
            fh.write(json.dumps(dict(user("10:05", "ok #23 " + WITNESS),
                                     sessionId="sans-cwd")) + "\n")
        out = self.run_script()
        self.assertTotal(out, 0, 0, 0)
        self.assertIn("0 session(s) du worktree principal lue(s)\n", out)

    # --- which coordinator messages belong to the task ----------------------

    def test_coordinator_messages_attached_to_the_task(self):
        self.session(MAIN, "coord",
                     user("10:00", "où en est #23 ? " + WITNESS),
                     user("10:02", "et #230, l'autre ? " + WITNESS),
                     user("10:04", "regarde 23-tache " + WITNESS),
                     assistant("10:05", text="La carte 23-tache attend ton feu vert plan."),
                     # A tool call alone, written as its own event: not an answer.
                     assistant("10:05"),
                     user("10:06", "ok " + WITNESS),
                     assistant("10:07", text="La #24 attend aussi."),
                     user("10:08", "ok " + WITNESS),
                     user("10:09", "et la météo ? " + WITNESS))
        # A session elsewhere is not read at all, even naming the task.
        self.session("/work/ailleurs", "free", user("10:03", "#23 " + WITNESS))
        out = self.run_script()
        # 10:00, 10:04, 10:06: one moment of 6 + 3 min.
        self.assertTotal(out, 9, 1, 3)
        self.assertIn("Écartés : 3 hors tâche, 0 hors fenêtre", out)

    def test_whole_coordinator_turn_attaches(self):
        # Claude Code writes one event per block: a turn made of a text naming
        # the task, a tool call (the watch relaunched), then a closing text
        # that does not, still names the task.
        self.session(MAIN, "coord",
                     assistant("10:00", text="La carte 23-tache attend ton feu vert recette."),
                     assistant("10:00"),
                     assistant("10:00", text="Veille relancée."),
                     user("10:02", "ok " + WITNESS))
        out = self.run_script()
        self.assertTotal(out, 3, 1, 1)

    def test_background_notification_opens_a_new_turn(self):
        # The watch wakes the coordinator: a task notification opens a turn of
        # its own. The "ok" answers the last one, which names #23 only, not
        # the earlier wake-up about 24-x left unanswered.
        notification = "<task-notification>veille</task-notification>"
        self.session(MAIN, "coord",
                     user("09:00", "lance #24"),
                     user("10:00", notification),
                     assistant("10:00", text="24-x attend ton feu vert plan."),
                     user("11:00", notification),
                     assistant("11:00", text="23-tache attend ton feu vert recette."),
                     user("11:02", "ok " + WITNESS))
        out = self.run_script()
        self.assertTotal(out, 3, 1, 1)
        out = self.run_script("--issue", "24", worktree="/work/projet-worktrees/24-x")
        # Only "lance #24" is kept: the "ok" is out of that task.
        self.assertTotal(out, 3, 1, 1)
        self.assertIn("1 hors tâche", out)

    def test_issue_given_with_its_hash(self):
        # "--issue #23", as the number is written everywhere else, is #23.
        self.session(MAIN, "coord", user("10:00", "ok #23 " + WITNESS))
        out = self.run_script("--issue", "#23")
        self.assertTotal(out, 3, 1, 1)

    # --- window -------------------------------------------------------------

    def test_window(self):
        self.session(MAIN, "s1",
                     user("09:00", "trop tôt #23"),
                     user("10:00", "dedans #23"),
                     user("12:00", "trop tard #23"))
        out = self.run_script("--since", at("09:30"), "--until", at("11:00"))
        self.assertTotal(out, 3, 1, 1)
        self.assertIn("2 hors fenêtre", out)

    def test_window_without_offset_is_local_time(self):
        # A window given as on a clock, with no offset, is the maintainer's
        # local time. TZ "UTC-2" is POSIX for UTC+2: 11:30-13:00 local is
        # 09:30Z-11:00Z. Read as UTC, the message kept would be 12:00Z's.
        self.session(MAIN, "s1",
                     user("09:00", "trop tôt #23"),
                     user("10:00", "dedans #23"),
                     user("12:00", "trop tard #23"))
        env ={k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
        env.update(HOME=os.path.join(self.root, "empty-home"), TZ="UTC-2")
        out = self.run_script("--since", f"{DAY}11:30", "--until", f"{DAY}13:00", env=env)
        self.assertTotal(out, 3, 1, 1)
        self.assertIn("- 2026-10-12 10:00Z → 10:00Z : 3 min\n", out)
        self.assertIn("2 hors fenêtre", out)

    def test_unreadable_window_is_an_error(self):
        for option in ("--since", "--until"):
            with self.subTest(option=option):
                done = subprocess.run([sys.executable, SCRIPT, "--main", MAIN,
                                       "--worktree", TASK, option, "hier"],
                                      capture_output=True, text=True, timeout=30)
                self.assertEqual(done.returncode, 2)
                self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
                self.assertIn("ISO 8601", done.stderr)
                self.assertEqual(done.stdout, "")

    # --- where the transcripts are -----------------------------------------

    def test_transcripts_folder_from_environment(self):
        self.session(MAIN, "s1", user("10:05", "ok #23"))
        env ={k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
        env["HOME"] = os.path.join(self.root, "empty-home")
        with self.subTest(source="CLAUDE_CONFIG_DIR"):
            out = self.run_script(transcripts=False,
                                  env=dict(env, CLAUDE_CONFIG_DIR=os.path.dirname(self.projects)))
            self.assertTotal(out, 3, 1, 1)
        with self.subTest(source="home"):
            home = os.path.join(self.root, "home")
            os.makedirs(os.path.join(home, ".claude"))
            shutil.copytree(self.projects, os.path.join(home, ".claude", "projects"))
            out = self.run_script(transcripts=False, env=dict(env, HOME=home))
            self.assertTotal(out, 3, 1, 1)

    def test_unreadable_lines_skipped(self):
        folder = os.path.join(self.projects, "x")
        os.makedirs(folder)
        with open(os.path.join(folder, "s1.jsonl"), "w", encoding="utf-8") as fh:
            fh.write("{ pas du json\n[1, 2]\n")
            fh.write(json.dumps(dict(user("10:05", "ok #23"), cwd=MAIN, sessionId="s1",
                                     timestamp="hier")) + "\n")
            fh.write(json.dumps(dict(user("10:06", "ok #23"), cwd=MAIN, sessionId="s1")) + "\n")
        out = self.run_script()
        self.assertTotal(out, 3, 1, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
