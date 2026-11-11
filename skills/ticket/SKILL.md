---
name: ticket
description: Take a ticket from reading it to its merged pull request, with its journal kept outside the conversation.
argument-hint: "[ticket id]"
disable-model-invocation: true
allowed-tools: Bash(python3 *journal.py*)
---

The ticket id, if any, is `$ARGUMENTS`. `JOURNAL` means
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/ticket/journal.py"`. Stage files are in
`${CLAUDE_PLUGIN_ROOT}/skills/ticket/stages/`. "The project file" is what `JOURNAL key`
lists under `project_files`; a personal file overrides the shared one, field by field.

- Talk to the user in their language. The journal's content is in that language too;
  its field names and section titles stay in English.
- Nothing is written to the tracker, except what the PR's closing line does on merge.

## Find where the ticket is

Run `JOURNAL key`. It fails (a detached HEAD, during a rebase for instance): say so and
stop. `project_files` is empty, or the project file has no `Base branch`: propose
`/jam:init`, and stop.

**On the project file's `Base branch`**, in any worktree, this is the main session. It
never creates or writes a journal.
- With an id: run `JOURNAL key --key <id>`. A journal exists: give the command to open
  its session, `cd <Worktree> && claude`, with `Worktree` read from
  `JOURNAL show --key <id>`. Archived: say the ticket is closed. Otherwise: read
  `stages/start.md` and follow it.
- Without an id: run `JOURNAL list`, and ask which ticket to start or reopen.

**On another branch, in the main worktree** (`main_worktree=yes`): say that tickets
start from the base branch, each in its own worktree, and stop.

**On another branch, in a linked worktree**: this is the ticket's session.
- With an id: `JOURNAL key --key <id>` must give the same `key=` as the branch;
  otherwise refuse: this session works on its own ticket only; to start that ticket,
  run `/jam:ticket <id>` in a session on the base branch.
- Archived: say the ticket is closed, and stop.
- No journal: read `stages/framing.md` and follow it.
- A journal at `closed` (an archive move that failed): run `JOURNAL close` again, with
  the same options.
- A journal: run `JOURNAL show`, say where things stand in three sentences (the goal,
  the stage, what `Resume here` says to do next), and wait for the user's go-ahead.
  Then read the file of the journal's stage and follow it.

## Move on

At the end of a stage: run `JOURNAL next`, then `JOURNAL set --stage <next>`, then read
the next stage's file and follow it. A small ticket never clears the conversation
(`clear_first=no`): go straight on. At `follow-up`, `next` answers `closed`: never set
that stage; the ticket ends with `JOURNAL close` once the PR is merged.

Read only the current stage's file: each one holds everything that stage needs.
