# jam

**A workflow for product builders working with coding agents.** It starts with the
ticket: framed with you, tests before code, reviewed by a fresh agent, checked, then a
pull request. Its memory is a journal kept outside the conversation, so a ticket survives
`/clear`, compaction, and days between sessions. Built to fit any stack and any tracker.

> **Status: early.** `/jam:init` and the journal script are written; the script is tested.
> `/jam:ticket`, its review subagent and the session-start hook are being written, small
> tickets first: the part of "How jam works" from "Starting a ticket" on describes what
> they will do. jam runs on Claude Code today.

## Where it is going

The ticket is the first piece. A ticket rarely stands alone: it belongs to a milestone or
a project in your tracker, and a decision made in one ticket binds the others. Next, jam
gives each ticket the context of its subject and the decisions already made there. Bug
hunting, support answers and new specifications will then draw on the same decisions.
See [docs/vision.md](docs/vision.md).

## How jam works

### The idea

A ticket can span several days and several conversations. A conversation forgets: `/clear` empties
it, compaction summarizes it. jam keeps what matters outside the conversation, in one
journal per ticket: the goal, what "done" means, the plan, every decision, and the next
thing to do. Every new session on the ticket starts from it.

jam hard-codes no tool. It runs the commands written in your repository's project file:
read a ticket, run the tests, open a pull request. To change tracker or stack, you change
that file.

### Setting up a repository: `/jam:init`

`/jam:init` reads your repository to fill the project file: your code host (GitHub, GitLab),
your tracker, the branch you develop from, the format of your branch names, the commands
that run tests and lint, and links to the files that already describe your project
(`CLAUDE.md`, specs, tool configs, PR templates). It links to them; it copies nothing.

It asks you where to keep the file and what is sensitive in your code, and only asks
about the rest when it hesitates, with what it detected as the recommended answer. It
runs none of the commands: the first ticket does, and a wrong one is fixed in the file.
Then it shows you the whole file and, once you confirm, writes it, either in the
repository (`.jam/project.md`, for you to commit on your base branch, so that new
worktrees have it) or outside it (`~/.jam/<repo-id>/project.md`), as you choose. It
touches no permission setting: the session asks you before each push and each pull
request.

It never commits, never pushes, never writes to your tracker or code host.

### Starting a ticket

From your main session (the one in your repository's main folder), `/jam:ticket 142` reads ticket 142, creates its branch and a
separate working copy (a git worktree), and gives you the command to open a session
there. All the work on the ticket happens in that session, which keeps the ticket's
journal; your main session keeps none. There, `/jam:ticket` creates the journal on the
first run, and later finds it from the branch, says where things stand in three
sentences, and waits for you.

If a tool of yours already creates worktrees and opens sessions in them, keep using it:
`/jam:ticket` follows what your `CLAUDE.md` says about it, or you create the worktree
yourself, on a branch named after the ticket (`fix/142-…`), and run `/jam:ticket` in its
session.

### What a ticket goes through

The session reads the ticket and the code, then proposes a size; you confirm it. The size
sets how much process the ticket gets.

A **medium** ticket, the usual case, goes through six stages:

1. **Framing.** You and the session agree on the goal, the done criteria (each one names
   the test that proves it), the product rules and the plan. Product questions come as
   short multiple-choice questions, recommended answer first, each with its cost. A fresh
   agent reviews the framing, with the same stopping rule as the code review below. You
   give the first green light: your explicit go-ahead.
2. **Code.** A subagent writes the tests first, checks that they fail, then writes the
   code. It lists the decisions the code made on its own; you settle them.
3. **Review.** The session updates the journal and asks you to run `/clear`, then
   `/jam:ticket`. The session that wrote the code would judge it by what it meant to do; a
   fresh one can only judge it by the ticket. A fresh agent reviews the diff against the
   plan and the criteria, and each finding is checked in the code before it is fixed. A
   finding is blocking only if it describes a concrete failure scenario or breaks a done
   criterion. The
   loop stops when a pass finds nothing blocking, after three rounds at most (a starting
   value, to be tuned on real tickets); then you decide.
4. **Acceptance.** `/clear` and `/jam:ticket` again. If the change is visible, an agent
   goes through it in a browser and attaches screenshots; then you get at most five
   points to check. You give the second green light.
5. **Delivery.** The session writes the ticket's lessons in the journal, from two
   questions: a trap in the code, and a friction with jam itself (noted as it happens,
   during the whole ticket). A lesson about the code can be moved to `CLAUDE.md` or the
   project file, with your agreement; those about jam are how jam improves. Then the
   session pushes and opens the pull request, asking you first.
6. **Follow-up.** The session checks CI. A comment from a human reviewer on the pull
   request sends the ticket back to the code. The merge is yours. Once merged, the journal
   is archived and jam gives you the commands to remove the working copy.

A **small** ticket gets three lines of framing (goal, done criterion, test). The session
writes the test, then the code itself; one quick review pass follows; there is no
`/clear`; you check the change if it is visible, and give one green light before the
pull request.

A **large** ticket is not available yet.

A ticket touching what your project file lists as sensitive (money, accounts, personal
data, migrations…) is never small, and its review gets one more pass focused on security
and data.

### An example

Ticket 142 asks for a CSV export of a month's stock movements. The session reads it and the code, and
proposes *medium*, not sensitive: the export holds no personal data; you confirm. During framing it asks one question: semicolon or comma
as separator? You pick semicolon. The done criteria name two tests. A fresh agent finds a
gap (cancelled movements), which you settle; first green light. The subagent writes both
tests, sees them fail, writes the export, and notes one decision it made alone: an empty
month gives a file with only the header. You accept it. `/clear`, `/jam:ticket`: the
review finds nothing blocking. `/clear`, `/jam:ticket`: the acceptance agent opens the
export page, downloads the file and attaches a screenshot; you check three points; second green light. The session
writes one lesson, asks before pushing, opens the pull request and checks CI; you merge,
and the journal is archived.

### What jam asks of you

On a medium ticket: confirm the size, frame it with the session, settle the decisions the
code made, run `/clear` twice, give two green lights, decide when a loop reaches three
rounds, agree to the push and the pull request, and merge.

At each pause, jam notes whether you accepted, corrected, or asked for an explanation. How
often you had to correct its work shows how well the workflow serves you.

### Where things live

- `<repo-id>` is a name derived from the repository's `origin` remote, such as
  `acme-shop`.
- The project file: in the repository, or in `~/.jam/<repo-id>/`, as chosen.
- Journals: always in `~/.jam/<repo-id>/`, never in the repository. When a ticket
  closes, its lessons about jam itself are also copied to `~/.jam/jam-lessons.md`, one
  file across all your repositories. A journal lives only on the machine where you
  work, so product decisions are copied into
  the pull request.
- When a session starts or resumes, and after `/clear` or a compaction, a hook gives
  Claude a short summary of the current ticket from its journal. It blocks nothing and
  writes nothing.

## Install

In Claude Code:

```
/plugin marketplace add jammindev/jam
/plugin install jam@jammindev
```

`/plugin install` lets you choose where the plugin is enabled. Updates from a third-party
marketplace are not automatic: update from `/plugin`. Then, in a repository:
`/jam:init`.

Requirements: `git` 2.31 or later, `python3` 3.9 or later, and a CLI for your forge
(`gh` or `glab`) so that jam can read tickets, open pull requests and see when they are
merged. Jira and Linear have not been tried yet.

`JAM_HOME` moves `~/.jam` elsewhere.

## Trust

A project file is code, like a Makefile: jam runs the commands it lists. Do not run jam on a repository, or a branch, whose project
file you do not trust, as you would not run its `make test`.

## Limitations

- Tested with Claude Code only.
- Two sessions writing the same journal at the same time can lose one write.
- A journal is not shared between machines.

## Development

The journal script is `skills/ticket/journal.py`, Python standard library only, with its
tests in `tests/`. Specs are in `docs/specs/`, decisions in `docs/decisions/`.

```
python3 -m pytest tests
ruff check .
```

## License

MIT
