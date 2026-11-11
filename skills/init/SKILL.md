---
name: init
description: Set jam up on the current repository by writing its project file and permission rules. Run once per repository, or again to refresh.
disable-model-invocation: true
---

Write the project file the `ticket` skill reads. Never commit, push, create a journal, or
write to the tracker or forge. `JOURNAL` below means
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/ticket/journal.py"`.

## Steps

1. **Prerequisites**: `git` 2.31+, `python3` 3.9+, a git repository; else stop and say
   what is missing. If a project file exists, this is an update: never rerun a command
   whose line is unchanged, never re-ask an answered question, show only differences,
   apply each with agreement, keep fields detection cannot see; no difference: say so
   and stop. Both files exist: update the shared one. Invalid `Ticket pattern`: prove a
   fix with `--pattern`, agree it with the user first.
2. **Detect**, noting each value's source: forge and CLI login (`gh`, `glab`), default
   branch, tracker, test, lint and run commands (prefer what CI runs), links. Propose
   only commands a file names; none: omit the field, do not ask. No `origin`: ask the forge in step 3.
   Ticket key: one shell loop over `git for-each-ref --sort=-committerdate --count=50
   --format='%(refname:lstrip=2)' refs/heads refs/remotes` (skip `*/HEAD`, strip `origin/`) prints each
   branch with the `key=` line of `JOURNAL key --branch "$b"`. Mostly numbers: no
   `Ticket pattern`. One shared prefix: propose it, checked with `--pattern 'ABC-\d+'`
   on two branches. Several: ask. `Ticket branch`: the format seen, else `{id}-{slug}`.
3. **Ask**, one message: the file from `project-template.md` (on update, only the
   differences), each line marked `detected (<source>)` or `to confirm`, marks unwritten; three questions at most,
   recommended first: shared or personal (shared if the user is the only recent
   committer; personal puts permission rules in global settings), what is sensitive,
   tracker or prefix if ambiguous. Ask agreement to run step 4; refused: all unverified.
4. **Prove** from the toplevel, Bash timeout 600000, keeping the exit code and last 20
   lines: tests and lint exit 0; reading an open ticket (from the list, or given by the
   user) prints its title; list (`--limit 5`) exits 0;
   `JAM_PR=<latest merged PR> /bin/sh -c '<PR state command>'` prints `merged`, stripped
   and lowercased (no merged PR: unverified). Never run the run command, the PR command
   or `Stage command`. Fix failures with the user. Above each command not proved, write
   `<!-- unverified: <reason> -->`.
5. **Confirm once, then write.** Shared mode: warn if not on the default branch, and if
   `git check-ignore` reports `.jam/project.md` or `.claude/settings.json` (then propose
   personal). Write the file whole: shared `.jam/project.md`; personal `project.md` two
   levels above the `journal=` path of `JOURNAL key --key setup` (create the directory).
   Merge into `.claude/settings.json` (shared) or `~/.claude/settings.json` (personal),
   under `permissions.ask`, without duplicates: `Bash(git push *)` and the PR command's
   prefix. Invalid JSON: write nothing.
6. **Summarize** what was written, what to commit, what is unverified; next:
   `/jam:ticket <id>`.

## Rules

- Fields the script reads are bold: `` - **Ticket pattern**: `ABC-\d+` `` (under
  Tickets), `PR state command`, `Stage command`.
- `Stage command`: personal file only, on request. One in a shared file: report it,
  never copy it.
- The project file stays under 60 lines, links by path, copies nothing.
  `Review: project checks` starts empty.
- Prose in the user's language; titles and field names in English.
