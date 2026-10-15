#!/usr/bin/env python3
"""Estimate the maintainer's time on one task from Claude Code transcripts.

    python3 scripts/maintainer_time.py --main <main worktree> --worktree <task worktree>
        [--issue <n>] [--since <ISO>] [--until <ISO>] [--transcripts <folder>]

--since and --until without an offset are local time.

The method's one measure (FR-055) is the time the maintainer spends on a task.
Nobody times it by hand, so this script rebuilds it from what they typed:

  - sessions read: those started in the main worktree, every one of them
    taken for the coordinator's (a free session opened there included),
    found in the transcripts folder (--transcripts, else
    $CLAUDE_CONFIG_DIR/projects, else ~/.claude/projects). The sessions of
    the task's worktree are not read: agents type there too (briefs, relays
    sent through a shell variable, pasted blocks), and no reading of those
    tells them from the maintainer's words. A transcript
    that cannot be read (broken link, rights, file gone) or carries no cwd
    is skipped;
  - messages kept: the maintainer's own words, read as the outbound guard
    reads them (hooks/guard_outbound.py, maintainer_words), minus sidechain
    events;
  - a message belongs to the task when it, or one of the coordinator's texts
    of its last turn before it (opened by the maintainer's previous message
    or by a background notification, such as the watch waking it), names
    #<issue> or the task's worktree (the folder name of --worktree);
  - messages less than 10 min apart form a moment, worth (last - first) plus
    3 min of reading.

Limits: the maintainer's acceptance test (recette), done in a session of the
task's worktree, is not counted, nor is a green light typed there; an "ok"
after a summary of several tasks counts for each; a message that names no
task is lost.

The report holds counts and times only, never a message's content: the
recetteur may version it in a public repo. It gives the number of the main
worktree's sessions read, so that a zero from a wrong path shows, and ends on
what it does not count.
"""
import argparse
import datetime
import json
import os
import re
import sys

# maintainer_words lives with the outbound guard: one reading of a transcript.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "hooks"))
from guard_outbound import maintainer_words  # noqa: E402

MOMENT_GAP = datetime.timedelta(minutes=10)
READING = datetime.timedelta(minutes=3)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, f"[jam] {self.prog} : {message}\n")


def iso(value):
    """A datetime from an ISO 8601 string, naive if it has no offset, or None."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def timestamp(value):
    """An aware datetime from a transcript's ISO timestamp (UTC, as Claude Code writes it), or None."""
    moment = iso(value)
    if moment is None:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=datetime.timezone.utc)


def window_bound(value):
    """An aware datetime from --since or --until, or None.

    Without an offset, the date is the maintainer's local time, as on their
    clock: read as UTC, a window given in Paris time would shift by two hours,
    and a wrong figure would enter the PR with no warning.
    """
    moment = iso(value)
    if moment is None:
        return None
    return moment if moment.tzinfo else moment.astimezone()


def transcripts_folder(given):
    if given:
        return given
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    base = config if config else os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "projects")


def read_sessions(folder, started_in):
    """{session id: [events]} for the *.jsonl under the folder started in started_in.

    The folder holds every project of the machine, and a session can weigh
    tens of MB: a file is dropped on its first cwd, before the rest is loaded.
    """
    sessions = {}
    for path, _, names in os.walk(folder):
        for name in sorted(names):
            if not name.endswith(".jsonl"):
                continue
            try:
                kept = read_transcript(os.path.join(path, name), started_in)
            except OSError:
                # A real folder holds broken links (a sub-agent's transcript
                # pointing to a folder since removed), and a file can lose its
                # rights or vanish while the folder is walked: one unreadable
                # file must not stop the measure.
                continue
            for event in kept:
                session = event.get("sessionId") or os.path.join(path, name)
                sessions.setdefault(session, []).append(event)
    return sessions


def read_transcript(path, started_in):
    """The events of one transcript, or [] if its first cwd is not started_in."""
    kept, cwd = [], None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            if cwd is None and isinstance(event.get("cwd"), str):
                # Resolved as --main is: a path through a link names the same worktree.
                cwd = os.path.realpath(event["cwd"])
                if cwd != started_in:
                    return []
            kept.append(event)
    # A session that cannot be placed is not the coordinator's: counted, it
    # would turn the zero of a mistyped --main into a measure.
    return kept if cwd is not None else []


def answer_text(event):
    """The text blocks of one of the agent's events, or ""."""
    if event.get("type") != "assistant" or not isinstance(event.get("message"), dict):
        return ""
    content = event["message"].get("content")
    if isinstance(content, list):
        content = "\n".join(b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text")
    return content.strip() if isinstance(content, str) else ""


def opens_turn(event):
    """True for a background task notification, such as the watch waking the agent.

    It opens a turn of its own, as a message of the maintainer does; a tool
    result belongs to the turn in progress.
    """
    if event.get("type") != "user" or not isinstance(event.get("message"), dict):
        return False
    content = event["message"].get("content")
    if isinstance(content, list):
        content = "\n".join(b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text")
    return isinstance(content, str) and ("<task-notification" in content
                                         or "SYSTEM NOTIFICATION" in content)


def coordinator_turns(events):
    """[(time, words, answers)] of the maintainer in one session, in order.

    answers are the agent's texts of its last turn before the message, opened
    by the maintainer's previous message or by a background notification.
    Claude Code writes one event per block, so a turn of "text, tool call,
    text" is several events, read in the file's order.
    """
    found, turn = [], []
    for event in events:
        if event.get("isSidechain"):
            continue
        words = maintainer_words(event)
        if words is None:
            if opens_turn(event):
                turn = []
                continue
            text = answer_text(event)
            if text:
                turn.append(text)
            continue
        moment = timestamp(event.get("timestamp"))
        if moment is not None:
            found.append((moment, words, turn))
        turn = []
    return sorted(found, key=lambda item: item[0])


def moments(times):
    """[(first, last)] of the messages less than MOMENT_GAP apart."""
    groups = []
    for moment in sorted(times):
        if groups and moment - groups[-1][1] < MOMENT_GAP:
            groups[-1][1] = moment
        else:
            groups.append([moment, moment])
    return [tuple(group) for group in groups]


def measure(sessions, worktree, issue, since, until):
    """(kept times, {why: count dropped}, sessions read) over the coordinator's sessions."""
    names = [re.escape(os.path.basename(worktree))]
    # "#23" as well as "23": the number is written with its # everywhere else.
    issue = (issue or "").lstrip("#")
    if issue:
        names.append(rf"#{re.escape(issue)}\b")
    names_task = re.compile("|".join(names))

    kept, dropped = [], {"hors tâche": 0, "hors fenêtre": 0}
    for events in sessions.values():
        for moment, words, turn in coordinator_turns(events):
            if not attached(words, turn, names_task):
                dropped["hors tâche"] += 1
            elif (since and moment < since) or (until and moment > until):
                dropped["hors fenêtre"] += 1
            else:
                kept.append(moment)
    return kept, dropped, len(sessions)


def attached(words, turn, names_task):
    """A coordinator message belongs to the task if it, or the turn it answers, names it."""
    return any(names_task.search(text) for text in [words, *turn])


def minutes(delta):
    return round(delta.total_seconds() / 60)


def report(kept, dropped, read):
    groups = moments(kept)
    total = sum((last - first + READING for first, last in groups), datetime.timedelta())
    lines = [f"[jam] Temps du mainteneur : {minutes(total)} min en {len(groups)} moment(s), "
             f"{len(kept)} message(s) retenu(s)",
             # A mistyped path reads no session: the zero must show it.
             f"{read} session(s) du worktree principal lue(s)"]
    for first, last in groups:
        lines.append(f"- {first.astimezone(datetime.timezone.utc):%Y-%m-%d %H:%M}Z → "
                     f"{last.astimezone(datetime.timezone.utc):%H:%M}Z : "
                     f"{minutes(last - first + READING)} min")
    lines.append(f"Écartés : {dropped['hors tâche']} hors tâche, "
                 f"{dropped['hors fenêtre']} hors fenêtre")
    # The figure is pasted into the PR: its main gap must travel with it.
    lines.append("Non comptés : recette du mainteneur et feux verts tapés "
                 "dans le worktree de la tâche")
    return "\n".join(lines)


def main():
    parser = Parser(prog="maintainer_time.py",
                    description="[jam] Temps du mainteneur sur une tâche, d'après les transcripts.")
    parser.add_argument("--main", required=True, help="chemin du worktree principal")
    parser.add_argument("--worktree", required=True,
                        help="chemin du worktree de la tâche (son nom rattache un message "
                             "à la tâche ; ses sessions ne sont pas lues)")
    parser.add_argument("--issue", help="numéro de l'issue (23 ou #23)")
    parser.add_argument("--since", help="début de la fenêtre, ISO 8601 ; sans fuseau, "
                                        "heure locale")
    parser.add_argument("--until", help="fin de la fenêtre, ISO 8601 ; sans fuseau, "
                                        "heure locale")
    parser.add_argument("--transcripts", help="dossier des transcripts (projects/)")
    args = parser.parse_args()

    since, until = window_bound(args.since), window_bound(args.until)
    if (args.since and since is None) or (args.until and until is None):
        parser.error("--since et --until attendent une date ISO 8601")
    folder = transcripts_folder(args.transcripts)
    if not os.path.isdir(folder):
        parser.error(f"dossier des transcripts introuvable ({folder})")

    # Transcripts hold absolute cwds: "." or a relative path would match none,
    # nor would a path through a link where Claude Code noted the physical one.
    sessions = read_sessions(folder, os.path.realpath(args.main))
    worktree = os.path.abspath(args.worktree)
    print(report(*measure(sessions, worktree, args.issue, since, until)))
    sys.exit(0)


if __name__ == "__main__":
    main()
