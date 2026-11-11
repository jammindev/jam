# Spec: the `init` skill, installing jam on a project

Status: accepted (maintainer's green light, 2026-11-11) · Target: first release, step 1 (skeleton)

## Why

The `ticket` skill knows no tool. Reading a ticket, running the tests, opening a PR: it
runs the commands written in the project file. Changing stack or tracker means changing
that file, not the plugin. `init` writes it, so that nobody has to learn its format.

A project file that looks right but holds a wrong command fails in the middle of a
ticket. So `init` proves each command by running it before writing it.

## What it produces

| Output | Shared mode | Personal mode |
|---|---|---|
| Project file | `<toplevel>/.jam/project.md`, to be committed | `<jam-dir>/project.md` |
| Permission rules | `<toplevel>/.claude/settings.json`, to be committed | `~/.claude/settings.json`, which applies to **every** repository of the user |

- **Shared** is for a repository the user owns or whose team adopts jam. **Personal** is
  for a repository where jam must leave no trace, such as a team repository where the
  user alone tries it.
- `<jam-dir>` is the grandparent of the `journal=` path printed by
  `journal.py key --key setup`. `init` never builds it from `JAM_HOME` itself.
- `init` writes these files and nothing else, except a `Stage command` the user asks for,
  which always goes to the personal file. It never commits, pushes or opens a PR,
  and creates no journal: journals belong to `ticket`.
- The skill is invoked as `/jam:init`. Its front matter sets
  `disable-model-invocation: true`, a Claude Code field, so that it never starts on its
  own; other tools ignore it.

## Principles

- **Link, never copy.** `CLAUDE.md`, `AGENTS.md`, tool configs (linter, formatter, test
  runner) and the forge's templates already say how the project works. The project file
  points to them by path and repeats nothing, so jam follows them when they change.
- **Detected before asked.** Every value the repository can tell is read from it. The
  user gets one message of questions, three at most, and one final confirmation.
- **Proved before written.** A command enters the file only after it ran successfully in
  this session, or with the user's explicit agreement to keep it unverified.
- **`init` writes nothing to the tracker or the forge.** It only reads from them.
- **Values reach commands as environment variables**, as in the journal spec. `{id}` in
  a ticket command is substituted by the model; it is safe because a key only holds
  `[A-Za-z0-9_.-]`.
- **The user's language** for prose in the file (sensitive areas). Section titles and
  field names stay in English: the script and the skills parse them.

## Requires from `journal.py`

One addition to the journal spec and script, needed to prove a `Ticket pattern` before it
is written:

- `key --branch <name>`: resolve the key as if `<name>` were the current branch;
- `key --pattern <regex>`: use this pattern instead of the project files' one.

Both only change what `key` prints; nothing is written.

## Steps

### 1. Check prerequisites

From the toplevel of the current worktree:

- `git` 2.31 or later and `python3` 3.9 or later; inside a git repository. Otherwise
  stop and say what is missing.
- An existing project file: `init` becomes an update (see "Running init again"). If
  `journal.py key` reports an invalid `Ticket pattern`, a fixed one is proved with
  `--pattern` and agreed with the user first.

### 2. Detect

Each detected value is kept with its source (file and line, or command).

| What | Where it is read |
|---|---|
| Forge, CLI and login | host of `origin`; `gh auth status` or `glab auth status` |
| Default branch | `git symbolic-ref refs/remotes/origin/HEAD`, else `main` or `master` |
| Branch format and ticket key | the last 50 branch names, local and remote |
| Tracker | forge issues if the repository has issues; a prefixed key in branch names hints at another tracker, to confirm |
| Test and lint commands | `Makefile`, `package.json` scripts, `pyproject.toml`, `tox.ini`, `noxfile.py`; CI files show which one CI runs |
| Run command | the same files (`dev`, `start`, `run` targets) |
| Links | `CLAUDE.md`, `.claude/CLAUDE.md`, `AGENTS.md`; linter, formatter and type checker configs; PR or MR templates |

**Ticket key.** Branch names are run through `journal.py key --branch`, in one shell
loop that prints each branch name, without its `origin/` prefix, with its `key=` line. If most ticket
branches give a numeric key, no `Ticket pattern` is written: the script's default applies. If they
carry one literal prefix (`ABC-123-…`, `feat/abc-123-…`), `init` proposes `ABC-\d+` and
checks it with `key --branch <name> --pattern 'ABC-\d+'` on two real branch names.
Several prefixes: the user chooses, in question 3. `Ticket branch` follows the format seen in branch
names, else `{id}-{slug}`.

**Commands are read, not guessed.** A command is proposed only if a file names it.
When several exist, the one CI runs comes first. When none exists, the field is left
out and no question is asked: `ticket` asks the first time it needs it.

### 3. Ask

One message: the project file `init` would write, each line marked `detected (<source>)`
or `to confirm` (marks are shown, never written), then at most three questions, each
with options and the recommended one first:

1. **Shared or personal?** Recommended: shared when the user is the only committer in
   the recent history, personal otherwise. Personal mode puts the permission rules in
   the user's global settings: say so.
2. **What is sensitive here?** A short list proposed from what the code shows (payments,
   authentication, personal data, migrations). A sensitive ticket is never `small` and
   gets one extra review pass.
3. **Which forge, tracker or ticket prefix?** Only when detection left one open (no
   `origin`: the forge).

The same message asks for agreement to run the commands of step 4: it lists them, says
why (a command enters the file only if it works) and that they may take minutes.

**Questions readable without jam's documentation.** The user often meets jam through
`init`. The message opens with two or three sentences: jam takes a ticket from reading
it to a PR (branch, tests, code, review), using a project file that lists the
repository's commands, `init` writes that file and rules that
make Claude ask before each push and each PR, and it commits nothing. Each question says in one sentence what it decides and
why jam needs it; each option says what it writes, where, and whom it affects. No jam
vocabulary: each choice is described by its effects. Permission rules are described
as what they do: ask before each push and each PR. The question tool is used when
available.

### 4. Verify by running

From the toplevel, with a 10-minute limit per command, keeping only the exit code and the
last lines of output:

- tests and lint: must exit 0;
- read a ticket: on one open ticket (from the list command, or a number the user gives),
  must print its title;
- list my tickets: must exit 0, even with no result;
- `PR state command`: run as `JAM_PR=<number> /bin/sh -c '<command>'`, as the script
  does, on the most recent merged PR, must print `merged` once stripped and lowercased; with no merged PR yet, it stays
  unverified;
- `Ticket pattern`: already checked in step 2.

Never run: the run command (it does not return), the command that opens a PR, and
`Stage command`. They are written with `<!-- unverified: never run by init -->` on the
line above. A failing command is corrected with the user and run again. One the
user keeps despite a failure (tests already red on the default branch, for instance) is
written with `<!-- unverified: <reason> -->` on the line above it.

### 5. Confirm and write

One final confirmation shows the project file and the permission rules to add. In shared
mode it also warns when:

- the current branch is not the default branch: other worktrees will not see the file
  until it is merged, so running `init` from the default branch is recommended;
- `git check-ignore` reports `.jam/project.md` or `.claude/settings.json` as ignored: the
  file would never be committed, so personal mode is proposed instead.

Then:

- the project file is written whole, at the path of the chosen mode;
- the settings file is merged, never replaced. Rules added to `permissions.ask`:
  `Bash(git push *)` and the prefix of the PR command (`Bash(gh pr create *)`,
  `Bash(glab mr create *)`). A rule already present is not duplicated. A settings file
  that is not valid JSON stops `init` before anything is written;
- the summary: files written, files to commit (shared mode), unverified commands, and
  the next step, `/jam:ticket <id>`.

The permission rules are a safety net, not a barrier: a variant such as `git -C . push`
escapes them. The README says so.

## The project file

Template: `skills/init/project-template.md`. The file stays short: it links, never copies,
and each line answers a need of the workflow.

```markdown
# Project

## Tickets
- Tracker: GitHub Issues
- Read a ticket: `gh issue view {id} --comments`
- List my tickets: `gh issue list --assignee @me`

## Code
- Base branch: main
- Ticket branch: {id}-{slug}
- Tests: `make test`
- Lint: `make lint`
- Run: `make dev`
- Open a PR: `gh pr create --fill --base main`
- **PR state command**: `gh pr view "$JAM_PR" --json state --jq .state`

## Sensitive (one extra review pass)
- Payment calculations, accounts and permissions, personal data, migrations

## Review: project checks

## Links
- Agent instructions: CLAUDE.md
- Lint config: pyproject.toml ([tool.ruff])
- PR template: .github/pull_request_template.md
```

- Only the bold fields are read by `journal.py` (`Ticket pattern`, `PR state command`,
  `Stage command`, see the journal spec), so they are always written in bold, such as
  ``- **Ticket pattern**: `ABC-\d+` `` under Tickets. Everything else is read by the model.
- **Review: project checks** starts empty. It is filled when a lesson is promoted at
  closing, never by `init`, so that nothing is copied from `CLAUDE.md`.
- **Links** is where `ticket` looks when a lesson deserves to outlive its ticket:
  promoting it to `CLAUDE.md`, to this file or to a linter rule is proposed at closing
  and written only with the user's agreement. That rule belongs to the `ticket` spec.
- `Stage command` is written only when the user asks for it, always in the personal file
  whatever the mode, marked unverified: it first runs on the next stage change.

## Running init again

- `init` detects again, never reruns a command whose line is unchanged (marked
  unverified or not), and never asks again what the user already answered (mode,
  sensitive areas, tracker). No difference: it says so and stops.
- It shows only the differences on detected fields, each with its source, and applies
  each one only with the user's agreement. Fields detection cannot see are kept.
- The mode is the file that exists. When both exist, detected fields are updated in the
  shared file and the personal file is left untouched.

## Trust

Running `init` runs the repository's commands (tests, scripts), as `make test` would.
The README says so: do not run `init` on a repository you do not trust. A shared project
file that sets `Stage command` is reported to the user and ignored, as the journal spec requires;
`init` never copies it into the personal file.

## Size

The project file stays short: it links, never copies.
`SKILL.md` has no word ceiling: a numeric ceiling made it drop rules of this spec. Its
length is checked at review instead, against two questions: does each rule answer a
need of this spec or a friction seen on a real ticket, and does any rule repeat
another?

## Out of scope for step 1

- Switching between shared and personal mode.
- An `Open a session` command (opening a terminal on a worktree): the `ticket` spec
  decides whether it exists.
- Writing anything to the tracker or the forge; installing a forge CLI or logging in.
- Monorepos with several test commands per package.
- Per-project model or effort settings for the subagents.
- Editing `CLAUDE.md`, `AGENTS.md` or any tool config.

## Done when

On a real repository (the roadmap's criterion, `docs/vision.md` step 1: `init` fills the project file without any
correction by hand):

- shared mode: every command in the file ran successfully or is marked unverified with
  a reason, and `init` itself adds no file other than `.jam/project.md` and
  `.claude/settings.json`;
- personal mode: `init` writes nothing inside the repository;
- `init` run again right after proposes no change and asks no question;
- on a ticket branch, `journal.py key` gives the expected key, and the read command of
  the project file prints that ticket.
