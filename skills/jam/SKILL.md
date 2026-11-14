---
name: jam
description: Set jam up on this repository, or take a ticket from reading it to its merged pull request, with its journal kept outside the conversation.
argument-hint: "[ticket id | init]"
disable-model-invocation: true
---

The argument is `$ARGUMENTS`: `init`, a ticket id, or nothing. `JOURNAL` means
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/jam/journal.py"`: write it in full in each
command, never through a shell variable (zsh would not split it). Stage files are in
`${CLAUDE_PLUGIN_ROOT}/skills/jam/stages/`. "The project file" is what `JOURNAL key`
lists under `project_files`; a personal file overrides the shared one, field by field.

- Talk to the user in their language, short status lines included: these files are in
  English, which is no reason to answer in English. The journal's content is in that
  language too; its field names and section titles stay in English.
- Nothing is written to the tracker, except what the PR's closing line does on merge,
  and an issue the user agrees to at follow-up.
- Record a lesson at once, when it happens; by the close it would be forgotten. When
  an instruction of jam fails, has to be worked around, or serves no purpose:
  `JOURNAL set --lesson "jam: …"`. A trap met in the project's code: `JOURNAL set
  --lesson "…"`, without `jam:`, which only marks lessons about jam itself.

## Set up, or find where the ticket is

The argument is `init`: read `${CLAUDE_PLUGIN_ROOT}/skills/jam/init.md` and follow it.

Otherwise, the argument is the ticket id, if any. Run `JOURNAL key`. It fails (a
detached HEAD, during a rebase for instance): say so and stop. `project_files` is
empty, or the project file has no `Base branch`:
- in a linked worktree (`main_worktree=no`): the shared file may be missing from this
  branch only (never pushed, or the branch is older than it). Say so, and ask before
  setting up here;
- otherwise: say that jam is not set up on this repository yet, then read
  `${CLAUDE_PLUGIN_ROOT}/skills/jam/init.md` and follow it; the ticket waits for the
  next `/jam`.

**On the project file's `Base branch`**, in any worktree, this is the main session. It
never creates or writes a journal.
- With an id: run `JOURNAL key --key <id>`. A journal exists: give the command to open
  its session, `cd <Worktree> && claude`, with `Worktree` read from
  `JOURNAL show --key <id>`. Archived: say the ticket is closed. Otherwise: read
  `stages/start.md` and follow it.
- Without an id: run `JOURNAL list`, and the project file's `List my tickets` if it has
  one, then ask which ticket to start or reopen.

**On another branch, in the main worktree** (`main_worktree=yes`): say that tickets
start from the base branch, each in its own worktree, and stop.

**On another branch, in a linked worktree**: this is the ticket's session.
- With an id: `JOURNAL key --key <id>` must give the same `key=` as the branch;
  otherwise refuse: this session works on its own ticket only; to start that ticket,
  run `/jam <id>` in a session on the base branch.
- Archived: say the ticket is closed, and stop.
- No journal: read `stages/framing.md` and follow it.
- A journal at `closed` (an archive move that failed): run `JOURNAL close` again, with
  the same options.
- A journal: run `JOURNAL show`, say where things stand in three sentences (the goal,
  the stage, what `Resume here` says to do next), and wait for the user's go-ahead.
  Then read the file of the journal's stage and follow it. At `framing`, the journal
  already exists: never run `JOURNAL init` again; a medium ticket reads
  `stages/framing-medium.md`, which says how to resume.

## Move on

At the end of a stage: run `JOURNAL next`, then `JOURNAL set --stage <next>`.
- `clear_first=no`: read the next stage's file and follow it.
- `clear_first=yes` (a medium ticket, before review and acceptance): write `Resume here`
  so that a new session can start that stage from the journal alone, then ask the user
  to run `/clear`, then `/jam`, and stop. The session that wrote the code must
  not review it or accept it: it would judge it by what it meant to do.

At `follow-up`, `next` answers `closed`: never set that stage; the ticket ends with
`JOURNAL close` once the PR is merged.

Read only the current stage's file: each one holds everything that stage needs
(`framing.md` sends a medium ticket on to `framing-medium.md`).
