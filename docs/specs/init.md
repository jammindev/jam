# Spec: setting jam up on a project (`/jam init`)

Status: accepted (maintainer's green light, 2026-11-11; reduced to its core on
2026-11-11, see "Why so small") · Target: first release, step 1 (skeleton)

## Why

jam knows no tool. Reading a ticket, running the tests, opening a PR: it
runs the commands written in the project file. Changing stack or tracker means changing
that file, not the plugin. `init` writes it, so that nobody has to learn its format.

## Why so small

A first version proved each command by running it, translated the README as an
introduction, handled updates difference by difference, a teammate meeting a committed
file, a missing forge CLI. Its skill grew to a long list of rules, and test runs showed
the model dropping some of them (the file preview, the introduction). Nothing yet needed
those cases: jam had not run a single ticket. So `init` keeps its core, and each case
returns when a real ticket shows the need. The first version stays in git history.

## What it produces

| Output | In the repository | Outside it |
|---|---|---|
| Project file | `<toplevel>/.jam/project.md`, to be committed | `<jam-dir>/project.md` |

- `<jam-dir>` is the grandparent of the `journal=` path printed by
  `journal.py key --key setup`.
- `init` writes this file and nothing else. It sets no permission rule: the user's
  own settings decide what Claude may run, and jam asks before a push or a PR.
  Rules may come back when a real use needs them. It never commits, pushes or opens a PR,
  writes nothing to the tracker or the forge, and creates no journal.
- It is invoked as `/jam init`, or by `/jam` on a repository with no project file; its
  steps live in `skills/jam/init.md`, read by the router of the `jam` skill (see
  `docs/specs/ticket.md`, "The router"). The skill has `disable-model-invocation: true`
  so that it never starts on its own.

## Principles

- **Link, never copy.** `CLAUDE.md`, `AGENTS.md`, tool configs and the forge's templates
  already say how the project works. The project file points to them by path.
- **Detected before asked.** Every value the repository can tell is read from it, and
  shown through a question or in the final file, never in a list of findings.
- **Project commands are read, not guessed.** Test, lint and run commands are proposed
  only if a file names them; CI's comes first. None: the field is left out, and `/jam`
  asks when it needs it. Forge commands (read, list, open a PR, PR state) come from the
  forge CLI; `PR state command` must print `merged` once a PR is merged; `PR size
  command` prints lines added, lines removed and files changed, and is written only when
  the forge CLI gives these figures (`gh` does).
- **The user's language** for prose in the file; section titles and field names stay
  in English, as the script and the skill parse them.
- **Not run by `init`.** A wrong command shows on the first ticket, where it is fixed in
  the file. Running tests at setup took minutes and failed for reasons unrelated to
  the command (a stack not started).

## Steps

1. **Prerequisites**: `git` 2.31+, `python3` 3.9+, a git repository. A project file
   already exists: the run updates the fields it detects, keeps everything else
   (`Review: project checks`, `Stage command`, lines added by hand), and the
   confirmation shows what changes.
2. **Detect**: forge and tracker (host of `origin`, forge CLI); base branch (the one most
   of the last 30 merged PRs target, else the default branch); test, lint and run
   commands (`Makefile`, `package.json`, `pyproject.toml`, `tox.ini`, `noxfile.py`, CI
   files); links; ticket key, by running `journal.py key --branch` on the last 50 branch
   names: mostly numeric keys need no `Ticket pattern`; one shared prefix (`ABC-123`)
   gives `ABC-\d+`, checked with `--pattern` on two branches. `Ticket branch` follows the
   format seen, else `{id}-{slug}`.
3. **Ask**, in one sentence of context (what jam does, more in the README), then:
   - where the file lives, always; in the repository is recommended when the recent
     commits are all the user's;
   - what is sensitive, always, several answers allowed: a ticket touching it gets one
     more review before its PR;
   - base branch, ticket branch format, test or lint command, only when detection
     hesitates.
   Each question says what it decides; each option says what it writes and where.
4. **Confirm and write**: the file as it will be written (on a rerun, the lines that
   change), one confirmation (with the question tool, the file
   sits in the `preview` of the option that writes it: a test run cut the text before
   the question down to one sentence and the file was never shown), corrections applied before
   writing (the changed lines are shown again).
5. **Summarize**: the file written, then the user's steps before the first ticket, in
   order (`init` itself never commits or pushes). When the current branch is not the
   base branch: `git switch <base>` (an uncommitted file follows; with the base checked
   out in another worktree, the file moves there, and so does the work). In the
   repository: commit the file on the base branch and push it, since `start` creates
   worktrees from `origin/<base>`. Then `/jam <id>`, from a session on the base
   branch. On a real repository, `init` ran on a branch other than the base, and gave
   `/jam <id>` as the next step, which the router refuses there; on another, the
   file was committed on the local base branch but not pushed.

## The project file

Template: `skills/jam/project-template.md`. The file stays short: it links, never copies,
and each line answers a need of the workflow.

```markdown
# Project

## Tickets
- Tracker: GitHub Issues
- Read a ticket: `gh issue view {id} --json title,body,comments --jq '.title, .body, (.comments[] | .author.login + ": " + .body)'`
- List my tickets: `gh issue list --assignee @me`

## Code
- Base branch: main
- Ticket branch: {id}-{slug}
- Tests: `make test`
- Lint: `make lint`
- Run: `make dev`
- Open a PR: `gh pr create --base main`
- **PR state command**: `gh pr view "$JAM_PR" --json state --jq .state`
- **PR size command**: `gh pr view "$JAM_PR" --json additions,deletions,changedFiles --jq '"\(.additions) \(.deletions) \(.changedFiles)"'`

## Sensitive (one extra review pass)
- Payment calculations, accounts and permissions, personal data, migrations

## Review: project checks

## Links
- Agent instructions: CLAUDE.md
- Specs: docs/specs/
- Lint config: pyproject.toml ([tool.ruff])
- PR template: .github/pull_request_template.md
```

- Only the bold fields are read by `journal.py` (`Ticket pattern`, `PR state command`,
  `PR size command`, `Stage command`, see the journal spec), so they are always written in bold, such as
  ``- **Ticket pattern**: `ABC-\d+` `` under Tickets. Everything else is read by the model.
- **Review: project checks** starts empty. It is filled when a lesson is promoted at
  closing, never by `init`, so that nothing is copied from `CLAUDE.md`.
- **Links** is where `/jam` looks when a lesson deserves to outlive its ticket:
  promoting it to `CLAUDE.md`, to this file or to a linter rule is proposed at closing
  and written only with the user's agreement. That rule belongs to the `ticket` spec.
- `init` never writes `Stage command`; the user adds it to a personal file by hand.

## Deferred until a real ticket needs it

- Permission rules asking before a push or a PR (the maintainer runs Claude without
  prompts; jam asks in the conversation).
- Running each command before writing it.
- An introduction to jam longer than one sentence (the README has it).
- Updates question by question; a teammate meeting a committed file.
- Switching between the two locations; monorepos; an `Open a session`
  command; per-project model settings.

## Done when

On a real repository (`docs/vision.md`, step 1):

- `init` asks two questions, plus one per value detection hesitates on, and writes a
  file the user does not have to correct by hand up to the first ticket, which runs its
  commands;
- in the repository: `init` adds no file other than `.jam/project.md`; outside it:
  nothing inside the repository;
- on a ticket branch, `journal.py key` gives the expected key, and the read command of
  the file prints that ticket.
