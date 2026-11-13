---
name: init
description: Set jam up on this repository - write its project file.
disable-model-invocation: true
---

Never commit, push, create a journal, or write to the tracker or forge. `JOURNAL` means
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/ticket/journal.py"`.

## Steps

1. **Prerequisites**: `git` 2.31+, `python3` 3.9+, a git repository; else stop and say
   what is missing. A project file already exists: this run updates the fields it
   detects and keeps everything else as it is (`Review: project checks`,
   `Stage command`, lines added by hand); step 4 shows what changes.
2. **Detect**, silently, from the repository's files and its forge CLI (`gh`, `glab`):
   - tracker, and the forge commands from its CLI: read a ticket, list my tickets, open
     a PR, `PR state command` (prints `merged` once the PR is merged);
   - base branch: the one most of the last 30 merged PRs target, else the default branch;
   - test, lint and run commands, only if a file names them (prefer what CI runs);
   - links: agent instructions, specs, tool configs, PR template;
   - ticket key: one shell loop runs `JOURNAL key --branch "$b"` on the 50 most recent
     local and remote branch names, `origin/` removed. Mostly numbers: no
     `Ticket pattern`. One shared prefix followed by digits (`ABC-123`): `ABC-\d+`,
     checked with `--pattern` on two branches. `Ticket branch`: the format seen, else
     `{id}-{slug}`.
3. **Ask**, with the question tool if available, detected value recommended and first.
   Each question says in one sentence what it decides; each option says what it writes
   and where. Start the message with one sentence: jam takes a ticket from reading it to
   a PR, using the file this command writes; more in the README.
   - Always: where the file lives. In the repository (`.jam/project.md`, to commit), or
     outside it (`<jam-dir>/project.md`, the repository untouched). Recommend the
     repository when the recent commits are all the user's, else outside.
   - Always: what is sensitive here, several answers allowed, proposed from the code
     (payments, accounts, personal data, migrations). A ticket touching it gets one more
     review before its PR.
   - Only when detection hesitates: base branch, ticket branch format, test or lint
     command. Branches with several prefixes (`feat/`, `fix/`…) are a hesitation:
     propose `{type}/{id}-{slug}` first.
4. **Confirm, then write.** Show the file, using `project-template.md` for its layout
   only (every value in it is an example), filled with the detected and answered
   values, fields with no value left out; on a rerun, show the lines that change. Ask
   once. With the question tool, the whole file goes in the `preview` of the option
   that writes it: text before a question may be cut short, the preview is always
   shown. If the user corrects something, apply it,
   show the changed lines and ask again. Then write the file at the chosen path.
   `<jam-dir>` is the grandparent directory of the `journal=` path of
   `JOURNAL key --key setup`; create it if needed. Write nothing else: no permission
   rule, no settings file.
5. **Summarize** in three lines: what was written; in the repository, to commit on the
   base branch so that new worktrees have it; next step `/jam:ticket <id>`.

## Rules

- No command is run to test it: the first ticket runs them.
- Fields the script reads are bold, as in the template: `PR state command`, and
  `` - **Ticket pattern**: `ABC-\d+` `` under Tickets when one is needed.
- The file links to other files by path and copies nothing from them.
  `Review: project checks` starts empty.
- Prose in the user's language; section titles and field names in English.
