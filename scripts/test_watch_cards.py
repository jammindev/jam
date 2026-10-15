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
import time
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


def now_ms(minutes_ago=0):
    """stateStartedAt as the real CLI gives it: integer milliseconds since epoch."""
    return int((time.time() - minutes_ago * 60) * 1000)


def agent(state, started=None, pane="pane-1", main_state=None, mode=None):
    """One agent row shaped like the fixture's, with its state fields replaced."""
    row = dict(fixture("worktree-ps")["result"]["worktrees"][1]["agents"][0])
    started = now_ms() if started is None else started
    row.update(state=state, stateStartedAt=started, paneKey=pane,
               mainAgent={"state": main_state or state, "stateStartedAt": started})
    if mode:
        row["workingMode"] = mode
    return row


def undated(row):
    """The agent without stateStartedAt: its card is dated by the script's clock,
    from its first idle read, whatever time the interpreters take to start."""
    del row["stateStartedAt"]
    del row["mainAgent"]["stateStartedAt"]
    return row


BLOCKED ="agent en attente d'une autorisation"
IDLE = "aucun agent au travail"


class WatchCardsTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="watch-cards-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.fake = FakeOrca(os.path.join(self.root, "fake"))

    def watch(self, *responses, project="jam", options=()):
        self.fake.respond("worktree ps", *responses)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ORCA_", "JAM_"))}
        env["JAM_ORCA_BIN"] = self.fake.binary
        return subprocess.run([sys.executable, SCRIPT, project, "--interval", "0.01",
                               *options],
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

    # --- a ▶ card whose agent is stuck: blocked ----------------------------

    def test_wakes_on_blocked_agent(self):
        # `waiting` is the state of an agent on a permission prompt: it can no
        # longer update its card, so only its state shows it.
        for label, row in (("state", agent("waiting")),
                           ("mainAgent", agent("working", main_state="waiting"))):
            with self.subTest(field=label):
                self.setUp()
                done = self.watch(ps(), ps({TASK: dict(agents=[row])}))
                cards = self.assertWoke(done, [f"{TASK} ({BLOCKED})"], polls=2)
                self.assertIn("- 22-tache · in-progress · ▶ implémenteur en cours", cards)

    def test_blocked_agent_once_per_episode(self):
        # Blocked at launch counts as already seen: a relaunched watch does not
        # wake again for the same prompt. The ⏸ of the main card ends the run.
        blocked = dict(agents=[agent("waiting")])
        done = self.watch(ps({TASK: blocked}), ps({TASK: blocked}),
                          ps({TASK: blocked, MAIN: comment("⏸ attente")}))
        self.assertWoke(done, [MAIN], polls=3)

    def test_blocked_again_is_a_new_episode(self):
        done = self.watch(ps({TASK: dict(agents=[agent("waiting")])}),
                          ps({TASK: dict(agents=[agent("working")])}),
                          ps({TASK: dict(agents=[agent("waiting")])}))
        self.assertWoke(done, [f"{TASK} ({BLOCKED})"], polls=3)

    def test_second_agent_blocked_wakes(self):
        # Episodes are per agent (paneKey): a second prompt is news.
        first = agent("waiting", pane="pane-1")
        done = self.watch(ps({TASK: dict(agents=[first])}),
                          ps({TASK: dict(agents=[first, agent("waiting", pane="pane-2")])}))
        self.assertWoke(done, [f"{TASK} ({BLOCKED})"], polls=2)

    def test_blocked_agent_named_beside_a_comment_change(self):
        # The comment changes (its 💬 calls the coordinator) at the read where
        # an agent enters `waiting`. Named only for the comment, the prompt
        # would count as seen by the relaunched watch, and never wake.
        working = dict(comment="▶ relecture tour 2 en cours · 💬 retour : x",
                       agents=[agent("working")])
        waiting = dict(comment="▶ relecture tour 2, 2 relecteurs · 💬 retour : x",
                       agents=[agent("waiting")])
        done = self.watch(ps({TASK: working}), ps({TASK: waiting}))
        self.assertWoke(done, [f"{TASK} ({BLOCKED})"], polls=2)

    # --- a ▶ card with no agent at work: idle ------------------------------

    def test_wakes_on_idle_card(self):
        # The last agent stopped just now: the card crosses the threshold
        # while the watch runs. 3 s leaves room for the first read, which
        # waits for two Python interpreters to start, even on a slow runner:
        # read beyond the threshold, the card would count as seen and never wake.
        idle = dict(agents=[agent("done")])
        done = self.watch(ps({TASK: idle}), options=("--idle-minutes", "0.05"))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.splitlines()[0],
                         f"[jam] Carte(s) à traiter : {TASK} ({IDLE} depuis 0.05 min)")

    def test_wakes_on_card_idle_beyond_threshold_once_its_last_worker_leaves(self):
        # The orchestrator's terminal closes; the other agent stopped 20 min
        # ago. The card is beyond N from its first idle read: no read sees the
        # age cross N, yet the card must wake. Only the read at launch counts
        # an age beyond N as seen. The third read ends a run that missed it.
        stale = agent("done", started=now_ms(20), pane="pane-2")
        done = self.watch(ps({TASK: dict(agents=[agent("working"), stale])}),
                          ps({TASK: dict(agents=[stale])}),
                          ps({TASK: dict(agents=[stale]), MAIN: comment("⏸ attente")}))
        self.assertWoke(done, [f"{TASK} ({IDLE} depuis 10 min)"], polls=2)

    def test_agent_still_blocked_after_threshold_is_named_so(self):
        # An agent on its prompt is not at work, so the card crosses the
        # threshold too. That second wake must say "blocked": for an idle card
        # the coordinator relaunches the orchestrator, which only awaits an
        # answer here. Same 3 s margin as above. Orca may report the wait on
        # mainAgent only, the row itself still "working": waiting wins. Each
        # row is dated when its case starts, so as not to begin beyond N.
        for label, fields in (("state", dict(state="waiting")),
                              ("mainAgent", dict(state="working", main_state="waiting"))):
            with self.subTest(waiting=label):
                self.setUp()
                done = self.watch(ps({TASK: dict(agents=[agent(**fields)])}),
                                  options=("--idle-minutes", "0.05"))
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(done.stdout.splitlines()[0],
                                 f"[jam] Carte(s) à traiter : {TASK} ({BLOCKED} depuis 0.05 min)")

    def test_wakes_on_card_without_any_agent(self):
        # No agent to date the card: the script's own clock, from its first read.
        done = self.watch(ps({TASK: dict(agents=[])}), options=("--idle-minutes", "0.01"))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"{TASK} ({IDLE}", done.stdout.splitlines()[0])

    def test_unreadable_start_falls_back_to_script_clock(self):
        # Only integer milliseconds are read. An ISO string dating from long
        # ago would mean "beyond N at launch", which never wakes; read as
        # unknown, the card is dated from the first read and wakes after N.
        for label, started in (("iso", "2020-01-01T00:00:00Z"), ("bool", True),
                               ("missing", None)):
            with self.subTest(value=label):
                self.setUp()
                row = agent("done")
                if started is None:
                    undated(row)
                else:
                    row["stateStartedAt"] = row["mainAgent"]["stateStartedAt"] = started
                done = self.watch(ps({TASK: dict(agents=[row])}),
                                  options=("--idle-minutes", "0.01"))
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertIn(f"{TASK} ({IDLE}", done.stdout.splitlines()[0])

    def test_no_idle_wake_before_threshold_or_beyond_it_at_launch(self):
        # Default threshold, 10 min. An agent done 2 min ago is not idle yet;
        # one done 20 min ago was already beyond the threshold at launch.
        for minutes in (2, 20):
            with self.subTest(minutes_ago=minutes):
                self.setUp()
                idle = dict(agents=[agent("done", started=now_ms(minutes))])
                done = self.watch(ps({TASK: idle}), ps({TASK: idle}),
                                  ps({TASK: idle, MAIN: comment("⏸ attente")}))
                self.assertWoke(done, [MAIN], polls=3)

    def test_working_agents_keep_the_card_awake(self):
        # working on either field, or a background wait (workingMode monitoring),
        # is work. Undated, the agents would date an idle card from the read at
        # launch, and the third read comes after the threshold (0.6 s): read as
        # idle, the card would wake with MAIN.
        for label, state, fields in (("working", "working", {}),
                                     ("main working", "done", dict(main_state="working")),
                                     ("monitoring", "done", dict(mode="monitoring"))):
            with self.subTest(agent=label):
                self.setUp()
                busy = dict(agents=[undated(agent(state, **fields)),
                                    undated(agent("done", pane="pane-2"))])
                late = ps({TASK: busy, MAIN: comment("⏸ attente")})
                late["sleep"] = 1
                done = self.watch(ps({TASK: busy}), ps({TASK: busy}), late,
                                  options=("--idle-minutes", "0.01"))
                self.assertWoke(done, [MAIN], polls=3)

    # --- cards that the two new wakes leave alone --------------------------

    def test_only_running_task_cards_watched_for_agents(self):
        # main, completed, ⏸, ⛔, a card with no state segment: neither a
        # blocked agent nor idleness wakes for them. The agents are undated:
        # watched, the card would be dated from its first idle read (the
        # second), and the fourth read, after the threshold, would wake for it.
        # That read also changes another card, which ends the run.
        cases = {
            "main": (MAIN, dict(comment="▶ coordinateur")),
            "completed": (TASK, dict(comment="▶ fini", workspaceStatus="completed")),
            "paused": (TASK, dict(comment="⏸ feu vert plan")),
            "blocked": (TASK, dict(comment="⛔ bloqué : quota")),
            "no state": (TASK, dict(comment="")),
        }
        for label, (name, fields) in cases.items():
            with self.subTest(card=label):
                self.setUp()
                quiet = [undated(agent("waiting", pane="pane-a")),
                         undated(agent("done", pane="pane-b"))]
                fields = dict(fields, agents=quiet)
                first = ps({name: dict(fields, agents=[agent("working")])})
                later = ps({name: fields})
                other, mark = (MAIN, "⏸ fin") if name == TASK else (TASK, "💬 question")
                end = ps({name: fields, other: comment(mark)})
                end["sleep"] = 1
                done = self.watch(first, later, later, end,
                                  options=("--idle-minutes", "0.01"))
                self.assertWoke(done, [other], polls=4)

    def test_durations_must_be_positive_and_finite(self):
        # nan passes a "<= 0" check: as --idle-minutes it never wakes, as
        # --interval it crashes time.sleep.
        for option in ("--idle-minutes", "--interval"):
            for value in ("0", "-1", "dix", "nan", "inf"):
                with self.subTest(option=option, value=value):
                    done = self.watch(ps(), options=(option, value))
                    self.assertEqual(done.returncode, 2)
                    self.assertTrue(done.stderr.startswith("[jam] "), done.stderr)
                    self.assertNotIn("Traceback", done.stderr)

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
