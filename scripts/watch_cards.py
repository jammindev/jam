#!/usr/bin/env python3
"""Wait until an Orca card of a project needs the coordinator, then list them.

    python3 scripts/watch_cards.py <project> [--interval s]

<project> is the repo name or the repo id, as `orca worktree ps` gives them.
The script reads the cards once to learn their state, then polls. It wakes
when the comment of a card that is not `completed` changes and then either:
  - its first segment (segments are separated by " · ") starts with ⏸ or ⛔:
    the task waits for the maintainer, or is blocked;
  - one of its segments starts with ✓ or 💬: a green light or a message the
    coordinator relays.
A card already in that state at launch does not wake it: only a change does.
A ✓ or 💬 segment stays on the card until the coordinator acknowledges it
(docs/process/README.md), so until then any other change of the comment, a
new ▶ state for instance, wakes it again.

Exit codes:
  0   -> a card needs attention; every card of the project is listed on stdout
  2   -> the Orca CLI failed or answered garbage, its list of worktrees was
         truncated (at launch or later), the project has no card, or the
         arguments are invalid
  130 -> interrupted (Ctrl+C)
"""
import argparse
import sys
import time

import orca_cli

SEPARATOR = " · "
WAITING = ("⏸", "⛔")   # first segment only
RELAYED = ("✓", "💬")   # any segment


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


def needs_coordinator(text):
    segments = [segment.strip() for segment in text.split(SEPARATOR)]
    return segments[0].startswith(WAITING) or any(s.startswith(RELAYED) for s in segments)


def describe(card):
    parts = (card.get("displayName"), card.get("workspaceStatus"), comment(card))
    return "- " + SEPARATOR.join(p for p in parts if isinstance(p, str) and p)


def watch(project, interval):
    cards = project_cards(project)
    if not cards:
        raise orca_cli.OrcaError(f"aucune carte pour le projet « {project} » "
                                 "(nom ou id du repo, comme dans orca worktree ps)")
    seen = {key(card): comment(card) for card in cards}
    while True:
        time.sleep(interval)
        cards = project_cards(project)
        woken = []
        for card in cards:
            text = comment(card)
            changed = seen.get(key(card)) != text
            seen[key(card)] = text
            if (changed and card.get("workspaceStatus") != "completed"
                    and needs_coordinator(text)):
                woken.append(card)
        if woken:
            names = ", ".join(str(card.get("displayName")) for card in woken)
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
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval doit être positif")
    try:
        watch(args.project, args.interval)
    except orca_cli.OrcaError as error:
        print(f"[jam] veille des cartes arrêtée : {error}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
    sys.exit(0)


if __name__ == "__main__":
    main()
