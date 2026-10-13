#!/usr/bin/env python3
"""Tests for watch_cards.py — wake the coordinator when a card needs it.

Each case runs the script as the coordinator would, against the fake Orca CLI
of fixtures/fake_orca.py: `orca worktree ps` answers a queue of successive
outputs built from fixtures/orca/worktree-ps.json, and the script polls fast.

Run: python3 -m unittest scripts.test_watch_cards
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.fixtures.fake_orca import FakeOrca, failure, fixture, garbage, reply

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "watch_cards.py")

TASK = "22-tache"      # a card of the "jam" project
MAIN = "jam"           # the project's main worktree, a card too
OTHER = "autre-tache"  # a card of another project


def ps(cards=None, truncated=False):
    """worktree ps output where cards[displayName] overrides that card's fields."""
    document = fixture("worktree-ps")
    for row in document["result"]["worktrees"]:
        row.update((cards or {}).get(row["displayName"], {}))
    document["result"]["truncated"] = truncated
    return reply(document)


def comment(text, **extra):
    return dict(comment=text, **extra)


class WatchCardsTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="watch-cards-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.fake = FakeOrca(os.path.join(self.root, "fake"))

    def watch(self, *responses, project="jam"):
        self.fake.respond("worktree ps", *responses)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ORCA_", "JAM_"))}
        env["JAM_ORCA_BIN"] = self.fake.binary
        return subprocess.run([sys.executable, SCRIPT, project, "--interval", "0.01"],
                              capture_output=True, text=True, env=env, timeout=30)

    def polls(self):
        return len([c for c in self.fake.calls() if c[:2] == ["worktree", "ps"]])

    def assertWoke(self, done, names, polls):
        self.assertEqual(done.returncode, 0, done.stderr)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "[jam] Carte(s) à traiter : " + ", ".join(names))
        self.assertEqual(self.polls(), polls)
        return lines[1:]

    # --- what wakes the coordinator --------------------------------------

    def test_wakes_on_pause(self):
        done = self.watch(ps(), ps({TASK: comment("⏸ feu vert plan attendu")}))
        cards = self.assertWoke(done, [TASK], polls=2)
        # Every card of the project is listed, none of the other project.
        self.assertEqual(cards, ["- jam · in-progress",
                                 "- 22-tache · in-progress · ⏸ feu vert plan attendu"])

    def test_wakes_on_blocked(self):
        done = self.watch(ps(), ps({TASK: comment("⛔ BLOQUÉ : tests rouges")}))
        self.assertWoke(done, [TASK], polls=2)

    def test_wakes_on_green_light_or_message_added(self):
        for mark in ("✓ feu vert merge : « ok merge »", "💬 question au mainteneur"):
            with self.subTest(mark=mark):
                self.setUp()
                done = self.watch(ps(), ps({TASK: comment("▶ implémenteur en cours · " + mark)}))
                self.assertWoke(done, [TASK], polls=2)

    def test_no_wake_while_working(self):
        # ▶ a -> ▶ b, and a ⏸ that is not the first segment: no wake. The
        # script only wakes on the fourth output.
        done = self.watch(ps(),
                          ps({TASK: comment("▶ relecteur en cours")}),
                          ps({TASK: comment("▶ relecteur · ⏸ pas en tête")}),
                          ps({TASK: comment("⏸ feu vert recette attendu")}))
        self.assertWoke(done, [TASK], polls=4)

    # --- what does not ---------------------------------------------------

    def test_card_already_waiting_at_launch_ignored(self):
        waiting = comment("⏸ feu vert merge attendu")
        done = self.watch(ps({TASK: waiting}), ps({TASK: waiting}),
                          ps({TASK: waiting, MAIN: comment("⛔ main en conflit")}))
        cards = self.assertWoke(done, [MAIN], polls=3)
        self.assertIn("- 22-tache · in-progress · ⏸ feu vert merge attendu", cards)

    def test_other_project_ignored(self):
        done = self.watch(ps(), ps({OTHER: comment("⏸ attente")}),
                          ps({OTHER: comment("⏸ attente"), TASK: comment("💬 question")}))
        cards = self.assertWoke(done, [TASK], polls=3)
        self.assertFalse([c for c in cards if OTHER in c])

    def test_completed_card_ignored(self):
        done_card = comment("⏸ fini", workspaceStatus="completed")
        done = self.watch(ps(), ps({TASK: done_card}),
                          ps({TASK: done_card, MAIN: comment("⏸ attente")}))
        self.assertWoke(done, [MAIN], polls=3)

    def test_project_by_repo_id(self):
        done = self.watch(ps(), ps({TASK: comment("⏸ attente")}), project="repo-jam")
        self.assertWoke(done, [TASK], polls=2)

    # --- failures --------------------------------------------------------

    def test_cli_fails(self):
        for label, responses in (("at launch", [failure()]),
                                 ("later", [ps(), failure()]),
                                 ("garbage", [ps(), garbage()])):
            with self.subTest(case=label):
                self.setUp()
                done = self.watch(*responses)
                self.assertEqual(done.returncode, 2)
                self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
                self.assertEqual(done.stdout, "")
                self.assertNotIn("Traceback", done.stderr)

    def test_truncated_list(self):
        # A card beyond the cut would never wake the coordinator: stop instead.
        # The later case also pauses a card, so that ignoring the cut would
        # wake (exit 0) rather than wait forever.
        for label, responses in (("at launch", [ps(truncated=True)]),
                                 ("later", [ps(), ps({TASK: comment("⏸ attente")},
                                                     truncated=True)])):
            with self.subTest(case=label):
                self.setUp()
                done = self.watch(*responses)
                self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
                self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
                self.assertIn("tronquée", done.stderr)
                self.assertEqual(done.stdout, "")

    def test_unknown_project(self):
        # A typo must not leave the coordinator waiting forever on nothing.
        done = self.watch(ps(), project="jma")
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
        self.assertIn("jma", done.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
