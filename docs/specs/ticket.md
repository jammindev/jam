# Spec: the `ticket` skill, from a ticket to its pull request

Status: draft · Target: first release, step 1 (skeleton), the small ticket first

## Why

A ticket spans days and conversations. `ticket` runs it from reading it to its merged
pull request, keeps its memory in the journal (`docs/specs/journal.md`), and stops to ask
the developer only for the decisions that are theirs. The README, section "How jam
works", describes the workflow as the user sees it; this spec says what each stage does,
what it writes to the journal, and when it stops.

## Scope of this first version

The path of a **small** ticket, end to end: starting it from the main session; three
lines of framing, the test then the code, one review pass by a fresh agent (and a
targeted one after a blocking fix), one green light; delivery, follow-up and closing.

The roadmap's first criterion is exactly this: a first small real ticket reaches its
green light before the pull request (`docs/vision.md`, step 1). The **medium** ticket
(framing review, the `implementer` subagent, the two clears, browser acceptance, the
extra review pass of a sensitive ticket) is specified once a real small ticket has run,
from what it showed.

ADR 0019 lists two subagents. Only `reviewer` is built now: on a small ticket the session
writes the code itself, and whether code is written by a subagent at all is an open
question of the vision (decided at step 3).

## How the skill is built

`init` showed the cost of one long skill: past a certain length, the model drops rules.
So:

- `skills/ticket/SKILL.md` is a short router. It finds where the ticket is, then reads
  **only** the file of the current stage.
- One file per stage, in `skills/ticket/stages/`: `start.md`, `framing.md`, `code.md`,
  `review.md`, `acceptance.md`, `delivery.md`, `follow-up.md`. Each says what the stage
  does, what it writes to the journal, and when it stops. None names the next stage
  (see "Moving on").
- Anything with one right answer comes from `journal.py`: key, journal path, whether the
  session is in the main worktree, stage, next stage, whether to clear first.
- `JOURNAL` below means `python3 "${CLAUDE_PLUGIN_ROOT}/skills/ticket/journal.py"`,
  written in full in each command, never through a shell variable (zsh would not split
  it);
  "the project file" means the merged result of the shared and personal files.

### Requires from `journal.py`

One addition to the journal spec and script: `key` also prints
`main_worktree=yes|no`, `yes` when the checkout is the repository's main worktree (its
git dir is the common git dir). The router uses it to refuse a ticket branch checked
out in the main worktree.

## The router: `/jam:ticket [<id>]`

The id, if any, is the skill's argument (`$ARGUMENTS`).

1. `JOURNAL key` gives the current branch, its key, `main_worktree`, and whether the
   journal exists or is archived. `key` fails (a detached HEAD, during a rebase for
   instance): say so and stop. No project file, or no `Base branch` in it: propose
   `/jam:init`, and stop.
2. **On the project file's `Base branch`, in any worktree**: the main session. The
   branch decides, not the worktree: with a bare repository, the main session is in a
   linked worktree on the base branch. A test
   run on a bare repository routed its main session to framing, on a ticket named after
   the base branch.
   - with an id: `JOURNAL key --key <id>`. A journal exists: give the command to open its
     session (`Worktree` from `JOURNAL show --key <id>`), nothing else. Archived: say the
     ticket is closed. Otherwise: read `stages/start.md`;
   - without an id: `JOURNAL list`, and ask which ticket to start or reopen.
   The main session never creates or writes a journal.
3. **On another branch, in the main worktree** (`main_worktree=yes`): say that tickets
   start from the base branch, each in its own worktree, and stop.
4. **On another branch, in a linked worktree**: the ticket's session.
   - with an id: `JOURNAL key --key <id>`; a `key=` that differs from the branch's:
     refused, the session works on its own ticket only; to start that ticket, run
     `/jam:ticket <id>` in a session on the base branch;
   - archived: say the ticket is closed, and stop;
   - no journal: read `stages/framing.md`;
   - a journal at `closed` (an archive move that failed): run `JOURNAL close` again, with
     the same options;
   - a journal: `JOURNAL show`, say where things stand in three sentences (goal, stage,
     `Resume here`), and wait for the user. On the go-ahead, read the file of the
     journal's stage.

### Moving on

At the end of a stage: `JOURNAL next`, then `set --stage <next>`, then read that stage's
file. A small ticket never clears (`clear_first=no`), so the session goes on. Only going
back is named in a stage file: acceptance → code, follow-up → code. At `follow-up`,
`next` answers `closed`: never `set --stage closed`; the ticket ends with `JOURNAL close`
once the PR is merged.

**Before handing back to the user**, the journal holds what changed in the turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. Every stage file of the ticket
session repeats this rule: a stale journal is the only way to lose work. It is tied to
the end of a turn, not to the `/clear`: after a `/clear` or a closed window the model
gets no turn, and no hook gives it one (`SessionEnd` runs a command, cannot block, and
the model never sees it).

## Stages

### Still worth doing?

A ticket picked from the backlog may be done, blocked or outdated. Finding out after a
worktree, a new environment and a full test run wastes a session (seen on a real
ticket: six minutes of tests before anyone asked). So, right after reading the ticket,
reading only and on this ticket only:

- already done: a merged PR names it, or the code already does what it asks;
- blocked: it depends on a ticket still open;
- outdated: the code it names is gone, or a later ticket or decision replaced it.

Nothing points to done, blocked or outdated: one line, and the stage goes on without a
question. Any sign of one, proven or only suspected: one to three lines with what shows
it, and the user decides whether to go on.
This is a check inside start and framing, not a stage. When start ran, framing checks
again: a cheap repeat, kept for worktrees made without start, and because start may
read a base branch older than the worktree's. jam closes no ticket and sorts no
backlog: closing the ticket is the user's call.

### start (main session)

1. Read the ticket with the project file's `Read a ticket` command. No such command: ask
   the user for its title and content. Then **check that it is still worth doing** (see
   "Still worth doing?"), before any branch or worktree exists.
   Then look for work already started on this ticket, whatever created it: a branch
   whose key is the ticket's, or a worktree on it. Found: reuse it, create nothing, and
   say so. A real run had two main sessions start the same ticket three minutes apart;
   only one worktree survived, by luck.
2. Build the branch name from `Ticket branch`: `{id}` is the ticket's id without `#`,
   `{slug}` a few words of the title in lowercase ASCII joined by `-`, and `{type}`,
   when the format has it, the kind of change (`feat`, `fix`…) among those seen in the
   repository's branches. Announce the name and go on, without waiting. On six real
   tickets the proposed name was asked about and
   accepted six times out of six, once after a minute's wait.
3. Check with `JOURNAL key --branch <name>` (without `--key`, which would win) that it
   gives the ticket's key. If not, typically a tracker key such as `ENG-142` without a
   `Ticket pattern`, say so and propose either rerunning `/jam:init` to add the pattern,
   or a branch named after the key itself.
4. When the project's own instructions (`CLAUDE.md`, the project's memory) say how to
   create a worktree or open a session, with a tool of the user's, follow them for this
   step and the next. jam names no such tool: the router only needs a ticket branch in
   a linked worktree, whoever created it. Otherwise,
   create the worktree next to this session's, at `<worktree>-<key>` (lowercased,
   `<worktree>` from `JOURNAL key`), from
   the project file's `Base branch`, after `git fetch origin`:
   - new branch: `git worktree add --no-track -b <branch> <path> origin/<base>`;
   - local branch already there: `git worktree add <path> <branch>`;
   - branch only on `origin`: `git worktree add -b <branch> <path> origin/<branch>`;
   - branch already checked out in a worktree (`git worktree list`): reuse that path.
5. Give the command that opens the ticket's session and starts framing:
   `cd <path> && claude "/jam:ticket"`: the ticket session finds the ticket from its
   branch, and the same command resumes it later. Say that jam must be enabled for that
   folder too: installed in user scope, or in project scope with `.claude/settings.json`
   committed on the base branch; not local scope. Write nothing else.

### framing

1. Read the ticket with `Read a ticket` (the id as the tracker writes it). No command:
   ask the user. A branch with no ticket behind it (`refactor/auth`): ask what it is for.
   Then check that it is still worth doing, as in start: the worktree may have been
   created by another tool, without start.
2. Read the code it touches. Propose a size with one sentence of reason, and say whether
   it is sensitive: it is when it touches an area listed under `Sensitive` in the
   project file.
   - Sensitive: only the medium flow fits, and it does not exist yet. Say so and stop.
   - Medium: say that only the small flow exists yet; the user may run it as small (a
     decision recorded once the journal exists) or stop.
3. Agree with the user on three lines: the goal, one done criterion, the test that proves
   it. The agreement is the go-ahead to write code, and the question says so: on a real
   ticket, the session went from framing to code while the project wanted an explicit
   go-ahead first. A product question the code cannot answer is asked as a short
   multiple-choice question, recommended answer first.
4. `JOURNAL init --size small --sensitive no` with `--title`, `--goal`,
   `--done-when "- [ ] <criterion> · proof: <test id>"` and `--resume` (the next action,
   such as "Write the failing test of …"); then the size decision, if any, and each
   product answer with `set --decision`.
5. Run the project file's `Tests` once on the untouched branch. A failure is not the
   ticket's: record it with `set --log`, and agree with the user how to go on (a missing
   `.env` or dependency in the new worktree, a red base branch).

### code

1. Write the test of the done criterion, run it, and check that it fails for the right
   reason. Then write the code until it passes.
2. Run `Tests` and `Lint` from the project file. A missing command: ask the user and
   offer to add it to the project file. A failure unrelated to the change: stop, show the
   end of the output, and agree a fix with the user.
3. Each decision the code made on its own:
   `set --decision "Decided by the code: … (to settle)"`.
4. When the test passes: `set --done-when` with the line ticked (`- [x]`). Commit on the
   ticket branch in the repository's style; the user's own settings may ask for
   agreement.

### review

1. The working tree must be clean (the code stage commits before review); otherwise the
   diff is shown to the user: a change the code stage did not make (a mutation left by
   an interrupted review, found by a later session) is restored, never committed; the
   rest is committed with their agreement, or the stage stops. One pass by the
   `reviewer` subagent, in the foreground: the session touches nothing in the worktree
   until it answers, since the reviewer may change and restore files. It is given: the
   ticket's text as `Read a ticket` prints it (or what the user gave at framing), the
   goal, the done criterion, the diff `origin/<base>...HEAD`, the project file's `Tests`
   command, its `Review: project checks`, and the paths under its `Links` that serve a
   review (agent instructions, a review grid, by its path; its steps are never copied
   in). Nothing else: on real tickets, sessions added "read the issue" or a project's
   review steps to the brief, which the reviewer's rules exclude, and it refused them;
   the ticket's text is now given instead.
2. Then `git status --porcelain` again: anything listed comes from the review (a
   mutation left behind by an interrupted reviewer, files the tests wrote); it is shown
   to the user, and tracked files are restored once they agree. The reviewer's own
   check only holds if it runs to the end; this one does not depend on it.
3. Check each finding in the code before acting on it. A finding is blocking only if it
   describes a concrete failure scenario or breaks the done criterion. Fix the blocking
   ones, rerun the tests, commit. A blocking fix gets a targeted pass, through steps 1
   and 2: the same brief, with the finding and the fix's diff (from the commit the
   previous pass reviewed, its `HEAD` then, to `HEAD`) in place of the whole diff.
   Repeat while a fix is blocking, three reviewer runs at most (`docs/vision.md`,
   principle 7); then the user decides. On a real ticket, the fix of a blocking finding
   changed approach and went to the PR unreviewed. The other findings, fixed or not, get
   no second pass.
4. `set --log "review: N blocking, M other"`, once per reviewer run, the targeted pass
   included.

### acceptance

The single green light of a small ticket, in one message of plain text, never inside
a question tool's form, and its answer is awaited as text. On five real tickets out of
six the acceptance came as a form alone: the text before a form can be hidden, and the
user asked how to log in to check the change.

The message holds:

- the goal and the criterion with its test;
- the decisions made by the code, to settle;
- what the review found, what was fixed, what was left;
- if the change is visible: at most three points to check, and how to see them (the
  project file's `Run` command, a page, a command).

The answer is recorded with `JOURNAL stop`:

- accepted as is: `stop seen` (or `explained` after an explanation); that is the green
  light;
- changed, or accepted with something to add: `stop corrected --note "…"`, then back
  to code (`set --stage code`); the flow
  comes back here with a new message and a new stop.

Each decision to settle gets one line, since `Decisions` only grows:
`set --decision "Settled: <decision> → kept"` or `→ changed: …`.

### delivery

1. Ask the user once, for the push and, if there is none yet, the PR: two separate
   agreements were asked on a real ticket, for one decision. jam sets no permission
   rule: the skill itself asks.
2. Push the branch: `git push -u origin <branch>`. No PR yet: open it with the project
   file's `Open a PR` command, adding a title and a body (`--title` and `--body-file -`
   reading stdin for `gh`, `--title` and `--description` for `glab`; never a body file
   inside the repository). The body follows the PR template under `Links` if there is
   one, and holds the goal, the criterion and its test, the product decisions, and
   `Closes #<id>` when the tracker is the forge's. Decisions live in the journal, on
   this machine only: the PR is where others see them. Then `set --pr <number>`, the
   bare number read from the command's output.
3. A PR already exists (back from follow-up): skip the PR, push only.

### follow-up

- Right after delivery, the PR's checks are watched in the background with the forge
  CLI (`gh pr checks <PR> --watch`, `glab ci status --live`), and their result is told
  to the user when they finish (no check reported yet: again a minute later). On two
  real tickets the user was the one who saw the CI fail, ten to twenty minutes after
  the PR. On resume or when asked: the checks again. A failing check is fixed on the
  branch, pushed with the user's agreement, and watched again.
- A human reviewer asks for a change: `set --decision` with the request, to settle, then
  `set --stage code`; the flow comes back through review, acceptance and delivery, which
  then only pushes.
- The merge is the user's. Once merged, before closing, one pass on the journal:
  - tick each box of `Done when` whose proof holds now (`set --done-when`); one that
    cannot be ticked is said to the user; if they decide to close anyway, its reason
    goes in with `set --decision`, then, at the close below,
    `--force --pending "<the box>"`;
  - the decisions taken since delivery (a merge order changed), and a red CI fixed
    with `set --log`;
  - **lessons**, with `set --lesson`, starting from those already noted during the
    ticket (`set --lesson` cannot take one back), from two separate questions. About the
    code or the project: a trap met on this ticket, which may be promoted, with the
    user's agreement, to `CLAUDE.md`, to the project file's `Review: project checks`, or
    to a linter rule. About jam: an instruction that failed, had to be worked around, or
    served no purpose, each lesson starting with `jam:`; none at all is written
    `jam: nothing to report`. At close, `journal.py` copies the others to
    `$JAM_HOME/jam-lessons.md` for the maintainer: removing a rule is as valid an
    outcome as adding one. The jam question recommends no answer: offered "nothing to
    add" as the recommended one, a session lost a friction the user had just met. A
    single question about "a friction in the workflow" was tried on the first real
    ticket: the session wrote only lessons about the code, while jam had failed four
    times. They are asked here, not at delivery: on a later ticket, the session closed
    straight after the merge, with the done criterion still unticked, and missed what
    follow-up had taught (a red CI, a merge order changed), then edited the archive by
    hand.
  - **what remains open** outside the code (review findings left aside, in the
    reviewer's answers; decisions still "to settle"; remarks out of the ticket's scope):
    one question lists them, and the user picks those that become an issue now. The
    session drafts each, shows it, and once they agree creates it with the CLI the
    project file's commands use (none: the draft goes to the user), then logs
    `issue <id>: <title>`. The others become `--pending` at the close. On a real ticket,
    two errors found by the review left as pending were never followed up.

  Then `JOURNAL close`. An archive is never edited: what was forgotten is told to the
  user. `close --force` only on the user's explicit request. Then the worktree and the
  branch are removed, from this session, once the user agrees, as its last action: the
  way the project's own instructions say (as in start, step 4), else, with
  `<main worktree>` read first from `git worktree list` (it fails once the session's
  folder is gone), in one command:
  `git -C <main worktree> worktree remove <path> && git -C <main worktree> branch -D <branch>` (`-D`, since a squash merge leaves it
  unmerged locally). Modified or untracked files, not ignored ones, make
  `worktree remove` refuse: they are shown, and `--force` waits for the user's
  agreement. The commands used to be given to the user, to run from the main session:
  on six real tickets out of six, the user handed the task back to the ticket session.

## The `reviewer` subagent

`agents/reviewer.md` in the plugin.

- Fresh context: it receives only what the review stage gives it, never the conversation.
  The ticket's text comes in that brief: the reviewer runs no tracker command.
- Tools: `Read`, `Grep`, `Glob`, and `Bash`, to read git and to run the project's tests.
  It may prove that a test guards a line by changing it, running the tests that cover
  it and restoring the file with `git restore`: one mutation at a time, only on a clean
  working tree, tracked files only, and only if the tests run on the worktree's own
  files. It never commits, pushes, switches branch, starts anything beyond the `Tests`
  command, or runs `git clean`, `git stash`, `git reset`, `git checkout` or `git add`
  (a model told to leave the tree clean could reach for them, discard work, or with
  `git clean -x` delete `.env` or `.venv`); what remains at the end is listed, never
  deleted. `Bash` itself is not
  restricted. Limiting it to `git diff`
  and `git log` was tried first: on a real ticket it ran none of the tests and
  mutations it was asked for and deduced them instead, and the session had to replay
  them. Each finding says whether it was proved by running something or deduced, and
  the answer ends with the tests and mutations run and the last `git status`.
- `model: opus`, `effort: xhigh`: review is where judgment is needed (`docs/vision.md`,
  principle 10). The alias follows the latest Opus; a subagent that applies a plan,
  such as the future `implementer`, gets `effort: medium`, with one rule: when the plan
  does not fit the code, it stops and reports what it found, instead of forcing its way
  (weakening a test, adding a workaround, changing the plan silently).
- It returns a list of findings, each with file and line, the failure scenario or the
  broken criterion, and `blocking` or `other`; or says there is none. No style remarks
  the linter already covers.

## Also in this version

- The session-start hook, exactly as the journal spec defines it.
- Journal content in the user's language; field names and section titles in English.
  Everything shown to the user is in their language, short status lines included: the
  skill's files are in English, and on six real tickets out of six the first line the
  user saw was English ("No journal: framing stage."). The router says it, and every
  stage file repeats it in its first line, start included.
- Nothing is written to the tracker, except what the PR's closing line does on merge,
  and an issue the user agrees to (see follow-up, what remains open).
- A jam instruction that fails, is worked around or serves no purpose is recorded at
  once as a `jam:` lesson, in any stage: by the close it would be forgotten. A trap met
  in the project's code is recorded at once too, without `jam:`: with a single channel,
  a session filed a code trap under `jam:`, and `set --lesson` cannot take it back.

## Out of scope for this version

- The medium ticket and the sensitive one (see "Scope").
- The large ticket; the level above the ticket.
- Copying decisions to the ticket in the tracker (the PR carries them).
- Reading past lessons at framing.
- Reviewing someone else's PR; a PR closed without merge.

## Done when

On a real repository with a project file:

- `/jam:ticket <id>` from the main session creates the branch and the worktree and gives
  the command to open the session; it writes no journal;
- in that session, a small real ticket goes through framing, code, review and acceptance
  to its green light, then delivery opens the PR after the user's agreement;
- a `/clear` in the middle, followed by `/jam:ticket`, resumes at the right stage from
  the journal alone;
- the journal holds the goal, the criterion and its test, the decisions, at least one
  lesson, and one stop line;
- after the merge, `close` archives the journal.
