#!/usr/bin/env python3
"""Wait until an Orca card of a project needs the coordinator, then list them.

    python3 scripts/watch_cards.py <project> [--interval s] [--idle-minutes n]

<project> is the repo name or the repo id, as `orca worktree ps` gives them.
The script reads the cards once to learn their state, then polls. It wakes
when the comment of a card that is not `completed` changes and then either:
  - its first segment (segments are separated by " · ") starts with ⏸ or ⛔:
    the task waits for the maintainer, or is blocked;
  - one of its segments starts with ✓ or 💬: a green light or a message the
    coordinator relays.
A card already in that state at launch does not wake it: only a change does.
A ✓ or 💬 segment stays on the card until the coordinator acknowledges it
(process/README.md), so until then any other change of the comment, a new ▶
state for instance, wakes it again.

It also wakes on a running task card (first segment ▶, neither the main
worktree nor `completed`) whose agents say what the comment cannot:
  - blocked: an agent enters the `waiting` state (`state` or
    `mainAgent.state`), the state of an agent on a permission prompt, which
    can no longer update its card;
  - idle: no agent at work (`working`, or `workingMode` = `monitoring`) for
    --idle-minutes. The card's age is now minus the latest `stateStartedAt`
    of its agents, integer milliseconds since the epoch; with no agent or no
    readable value, the script's own clock since it first saw the card so.
Both wake once per episode, with no state file: an agent already blocked at
launch, or a card already idle beyond the threshold at launch, counts as seen.
So an agent blocked between the script's exit and its relaunch is reported
only N minutes into its wait: the coordinator relaunches the watch at once,
before handling the wake.
After launch, an idle card wakes when its age reaches the threshold, or at
once if it is already beyond it at its first idle read. A card
with no agent is dated from launch, so it may wake again N minutes after a
relaunch: the coordinator then relaunches its orchestrator or marks it ⛔.
A blocked agent (waiting in state or in mainAgent.state) leaves no one at
work either, even if its other field says working: still blocked N minutes into
its wait, it wakes again, named "agent en attente d'une autorisation depuis
N min", so that the coordinator warns the maintainer rather than relaunch.
Orca's fourth state, `blocked`, whose meaning is not established, counts as
neither at work nor waiting: a choice, so such an agent wakes as idle.

Exit codes:
  0   -> a card needs attention; every card of the project is listed on stdout
  2   -> the Orca CLI failed or answered garbage, its list of worktrees was
         truncated (at launch or later), the project has no card, or the
         arguments are invalid
  130 -> interrupted (Ctrl+C)
"""
import argparse
import math
import sys
import time

import orca_cli

SEPARATOR = " · "
WAITING = ("⏸", "⛔")   # first segment only
RELAYED = ("✓", "💬")   # any segment
RUNNING = "▶"           # first segment of a card whose agents are watched
BLOCKED = "agent en attente d'une autorisation"


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, f"[jam] {self.prog} : {message}\n")


def project_cards(project):
    result = orca_cli.call("worktree", "ps")
    rows = result.get("worktrees")
    if not isinstance(rows, list):
        raise orca_cli.OrcaError("orca worktree ps : réponse inattendue")
    if result.get("truncated"):
        # A card beyond the cut would never wake the coordinator.
        raise orca_cli.OrcaError("liste des worktrees tronquée : des cartes peuvent manquer")
    return [row for row in rows if isinstance(row, dict)
            and project in (row.get("repo"), row.get("repoId"))]


def key(card):
    return card.get("worktreeId") or card.get("path") or card.get("displayName")


def comment(card):
    value = card.get("comment")
    return value if isinstance(value, str) else ""


def segments(text):
    return [segment.strip() for segment in text.split(SEPARATOR)]


def needs_coordinator(text):
    parts = segments(text)
    return parts[0].startswith(WAITING) or any(s.startswith(RELAYED) for s in parts)


def describe(card):
    parts = (card.get("displayName"), card.get("workspaceStatus"), comment(card))
    return "- " + SEPARATOR.join(p for p in parts if isinstance(p, str) and p)


# --- agents of a running card ------------------------------------------------

def running(card):
    return (segments(comment(card))[0].startswith(RUNNING)
            and card.get("isMainWorktree") is not True
            and card.get("workspaceStatus") != "completed")


def agents(card):
    rows = card.get("agents")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def states(agent):
    main = agent.get("mainAgent")
    return agent.get("state"), main.get("state") if isinstance(main, dict) else None


def blocked_panes(card):
    """paneKeys of the card's agents waiting on a prompt."""
    return {str(agent.get("paneKey")) for agent in agents(card) if "waiting" in states(agent)}


def at_work(agent):
    # Waiting on either field wins: an agent both blocked and "working" would
    # never reach the "still blocked N minutes into its wait" wake.
    if "waiting" in states(agent):
        return False
    return "working" in states(agent) or agent.get("workingMode") == "monitoring"


def started_at(agent):
    """Latest readable stateStartedAt of an agent, in seconds, or None.

    Orca gives integer milliseconds; anything else (an ISO string, a bool) is
    unreadable, and the card falls back on the script's clock.
    """
    main = agent.get("mainAgent")
    values = [agent.get("stateStartedAt"),
              main.get("stateStartedAt") if isinstance(main, dict) else None]
    readable = [v / 1000 for v in values if isinstance(v, int) and not isinstance(v, bool)]
    return max(readable, default=None)


class Watch:
    """What the previous read saw, to wake on transitions only."""

    def __init__(self, idle_seconds):
        self.idle_seconds = idle_seconds
        self.comments = {}   # card key -> comment
        self.blocked = {}    # card key -> paneKeys blocked at the previous read
        self.idle_age = {}   # card key -> idle age at the previous read, or absent
        self.idle_since = {}  # card key -> script clock when first seen idle, undated

    def idle_age_now(self, card, now):
        """Seconds the running card has had no agent at work, or None if it has one."""
        if any(at_work(agent) for agent in agents(card)):
            self.idle_since.pop(key(card), None)
            return None
        latest = max((s for s in map(started_at, agents(card)) if s is not None), default=None)
        if latest is None:
            latest = self.idle_since.setdefault(key(card), now)
        else:
            self.idle_since.pop(key(card), None)
        return now - latest

    def read(self, cards, now):
        """Record this read; return [(card, reason)] for the cards that wake.

        The reason names a blocked or idle agent, even when the comment
        changed at the same read; it is None for a comment change alone. The caller
        ignores what the read at launch returns: that state counts as seen.
        """
        woken = []
        for card in cards:
            k = key(card)
            text = comment(card)
            changed = self.comments.get(k) != text
            self.comments[k] = text

            if running(card):
                blocked, age = blocked_panes(card), self.idle_age_now(card, now)
            else:
                # Leaving ▶ ends both episodes: a later ▶ starts afresh.
                blocked, age = set(), None
                self.idle_since.pop(k, None)
            new_blocked = blocked - self.blocked.get(k, set())
            self.blocked[k] = blocked
            previous_age = self.idle_age.pop(k, None)
            if age is not None:
                self.idle_age[k] = age

            reason = None
            if new_blocked:
                reason = BLOCKED
            elif (age is not None and age >= self.idle_seconds
                  and (previous_age is None or previous_age < self.idle_seconds)):
                # previous_age is None at the first idle read: a card whose
                # last worker leaves after the others stopped long ago is
                # already beyond N, and wakes now or never. Only the read at
                # launch counts that as seen, by ignoring what it returns.
                # An agent still on its prompt leaves no one at work, but the
                # card is not idle: named so, the coordinator warns the
                # maintainer instead of relaunching an orchestrator that only
                # awaits an answer.
                what = BLOCKED if blocked else "aucun agent au travail"
                reason = f"{what} depuis {self.idle_seconds / 60:g} min"
            # A comment change needs no name (the listing shows the comment),
            # but must not hide the agents' reason: the relaunched watch
            # counts what this read saw as seen, and would never name it.
            if reason or (changed and card.get("workspaceStatus") != "completed"
                          and needs_coordinator(text)):
                woken.append((card, reason))
        return woken


def watch(project, interval, idle_minutes):
    cards = project_cards(project)
    if not cards:
        raise orca_cli.OrcaError(f"aucune carte pour le projet « {project} » "
                                 "(nom ou id du repo, comme dans orca worktree ps)")
    state = Watch(idle_minutes * 60)
    state.read(cards, time.time())
    while True:
        time.sleep(interval)
        cards = project_cards(project)
        woken = state.read(cards, time.time())
        if woken:
            names = ", ".join(str(card.get("displayName")) + (f" ({reason})" if reason else "")
                              for card, reason in woken)
            print(f"[jam] Carte(s) à traiter : {names}")
            for card in cards:
                print(describe(card))
            return


def main():
    parser = Parser(prog="watch_cards.py",
                    description="[jam] Attend qu'une carte Orca du projet demande le coordinateur.")
    parser.add_argument("project", help="nom ou id du repo")
    parser.add_argument("--interval", type=float, default=30.0,
                        help="secondes entre deux lectures des cartes (30 par défaut)")
    parser.add_argument("--idle-minutes", type=float, default=10.0,
                        help="minutes sans agent au travail avant de réveiller pour "
                             "une carte ▶ (10 par défaut)")
    args = parser.parse_args()
    # nan passes "<= 0": as --idle-minutes it would never wake, as --interval
    # it would crash time.sleep.
    if not (math.isfinite(args.interval) and args.interval > 0):
        parser.error("--interval doit être un nombre positif")
    if not (math.isfinite(args.idle_minutes) and args.idle_minutes > 0):
        parser.error("--idle-minutes doit être un nombre positif")
    try:
        watch(args.project, args.interval, args.idle_minutes)
    except orca_cli.OrcaError as error:
        print(f"[jam] veille des cartes arrêtée : {error}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
    sys.exit(0)


if __name__ == "__main__":
    main()
