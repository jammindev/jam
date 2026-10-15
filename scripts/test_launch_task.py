#!/usr/bin/env python3
"""Tests for launch_task.py — start a role in a task's worktree, under a cap.

Each case runs the script against the fake Orca CLI of fixtures/fake_orca.py
and checks the exact calls it made. The terminal list fixture holds four
terminals: two live agents (the coordinator of "jam" and an agent of another
project), a plain shell and a disconnected agent, both in a "jam" worktree.

Run: python3 -m unittest scripts.test_launch_task
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.fixtures.fake_orca import FakeOrca, failure, fixture, reply

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "launch_task.py")

REPO = "repo-jam"
NEW_ID = "repo-jam::/work/jam-worktrees/23-nouvelle"
EXISTING_ID = "repo-jam::/work/jam-worktrees/22-tache"
HANDLE = fixture("terminal-create")["result"]["terminal"]["handle"]
BRIEF = ("Tu es l'implémenteur de l'issue #23.\n"
         "Lis « /plugin/roles/implementeur.md »,  puis le plan.\n"
         "Critère de fin : $(tests) au vert ; \"IMPLÉMENTATION PRÊTE\".")
COMMAND = "claude --permission-mode dontAsk"


class LaunchTaskTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="launch-task-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.fake = FakeOrca(os.path.join(self.root, "fake"))
        for command, name in (("terminal list", "terminal-list"),
                              ("worktree ps", "worktree-ps"),
                              ("worktree create", "worktree-create"),
                              ("terminal create", "terminal-create"),
                              ("terminal wait", "terminal-wait"),
                              ("terminal send", "terminal-send")):
            self.fake.respond(command, reply(fixture(name)))
        self.brief = os.path.join(self.root, "brief.md")
        with open(self.brief, "w", encoding="utf-8") as fh:
            fh.write(BRIEF)

    def launch(self, *extra, worktree="23-nouvelle", role="implementeur", cap="5"):
        args = ["--repo", REPO, "--worktree", worktree, "--role", role,
                "--command", COMMAND, "--brief", self.brief, "--cap", cap, *extra]
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ORCA_", "JAM_"))}
        env["JAM_ORCA_BIN"] = self.fake.binary
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True,
                              text=True, env=env, timeout=30)

    def assertRefused(self, done, code, calls):
        self.assertEqual(done.returncode, code, done.stdout + done.stderr)
        self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
        self.assertNotIn("Traceback", done.stderr)
        self.assertEqual(self.fake.calls(), calls)

    def tail_calls(self, worktree_id, title="implementeur", role="implementeur"):
        return [
            ["terminal", "create", "--worktree", "id:" + worktree_id, "--title", title,
             "--command", f"JAM_ROLE={role} {COMMAND}", "--json"],
            ["terminal", "wait", "--terminal", HANDLE, "--for", "tui-idle",
             "--timeout-ms", "60000", "--json"],
            ["terminal", "send", "--terminal", HANDLE, "--text", BRIEF, "--enter", "--json"],
        ]

    # --- the happy paths -------------------------------------------------

    def test_creates_worktree_then_starts_role(self):
        done = self.launch()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(done.stdout.startswith("[jam] "), done.stdout)
        self.assertIn(HANDLE, done.stdout)
        self.assertEqual(self.fake.calls(), [
            ["terminal", "list", "--json"],
            ["worktree", "ps", "--json"],
            ["worktree", "create", "--repo", "id:" + REPO, "--name", "23-nouvelle",
             "--no-parent", "--json"],
        ] + self.tail_calls(NEW_ID))

    def test_existing_worktree_reused(self):
        done = self.launch(worktree="22-tache")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.fake.calls(),
                         [["terminal", "list", "--json"], ["worktree", "ps", "--json"]]
                         + self.tail_calls(EXISTING_ID))

    def test_same_name_in_another_repo_not_reused(self):
        done = self.launch(worktree="autre-tache")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(["worktree", "create", "--repo", "id:" + REPO, "--name", "autre-tache",
                       "--no-parent", "--json"], self.fake.calls())

    def test_title_and_role(self):
        done = self.launch("--title", "relecteur 2", role="relecteur")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.fake.calls()[3:],
                         self.tail_calls(NEW_ID, title="relecteur 2", role="relecteur"))

    # --- the caps: refused before any other call --------------------------

    def test_global_cap(self):
        # Two live agents: the plain shell and the disconnected agent do not count.
        self.assertEqual(self.launch(cap="3").returncode, 0)
        self.setUp()
        done = self.launch(cap="2")
        self.assertRefused(done, 1, [["terminal", "list", "--json"]])
        self.assertIn("2", done.stderr)

    def test_project_cap(self):
        # One live agent in "jam" (its coordinator), one in another project.
        self.assertEqual(self.launch("--project-cap", "2").returncode, 0)
        self.setUp()
        done = self.launch("--project-cap", "1")
        self.assertRefused(done, 1, [["terminal", "list", "--json"]])

    def test_truncated_terminal_list_refused(self):
        listing = fixture("terminal-list")
        listing["result"]["truncated"] = True
        self.fake.respond("terminal list", reply(listing))
        self.assertRefused(self.launch(), 1, [["terminal", "list", "--json"]])

    def test_truncated_worktree_list_refused(self):
        # The worktree may exist beyond the list: creating it would make a twin.
        listing = fixture("worktree-ps")
        listing["result"]["truncated"] = True
        self.fake.respond("worktree ps", reply(listing))
        self.assertRefused(self.launch(), 1, [["terminal", "list", "--json"],
                                              ["worktree", "ps", "--json"]])

    # --- bad input and CLI failures --------------------------------------

    def test_created_worktree_without_id(self):
        self.fake.respond("worktree create",
                          reply({"id": "req", "ok": True, "result": {"worktree": {}}}))
        done = self.launch()
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
        self.assertNotIn("Traceback", done.stderr)
        self.assertNotIn(["terminal", "create"], [c[:2] for c in self.fake.calls()])
        self.assertIn(["worktree", "create"], [c[:2] for c in self.fake.calls()])

    def test_role_restricted(self):
        for role in ("Implementeur", "relecteur;rm", "rôle", ""):
            with self.subTest(role=role):
                self.assertRefused(self.launch(role=role), 2, [])

    def test_missing_brief(self):
        os.remove(self.brief)
        self.assertRefused(self.launch(), 2, [])

    def test_brief_not_utf8(self):
        with open(self.brief, "wb") as fh:
            fh.write("Brief accentué : é".encode("latin-1"))
        self.assertRefused(self.launch(), 2, [])

    def test_cli_fails(self):
        self.fake.respond("terminal list", failure())
        self.assertRefused(self.launch(), 2, [["terminal", "list", "--json"]])

    def test_agent_not_ready_no_brief_sent(self):
        waited = fixture("terminal-wait")
        waited["result"]["wait"]["satisfied"] = False
        self.fake.respond("terminal wait", reply(waited))
        done = self.launch()
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
        self.assertIn(HANDLE, done.stderr)
        self.assertNotIn("send", [c[1] for c in self.fake.calls()])

    def test_brief_not_accepted(self):
        sent = fixture("terminal-send")
        sent["result"]["send"]["accepted"] = False
        self.fake.respond("terminal send", reply(sent))
        done = self.launch()
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
