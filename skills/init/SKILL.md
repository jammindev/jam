---
name: init
description: Set jam up on this repository, or refresh it - write its project file and permission rules.
disable-model-invocation: true
---

Never commit, push, create a journal, or write to the tracker or forge. `JOURNAL` means
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/ticket/journal.py"`.

## Steps

1. **Prerequisites**: `git` 2.31+, `python3` 3.9+, a git repository; else stop and say
   what is missing. If a project file exists, this is an update: rerun no command whose
   line is unchanged, re-ask nothing already answered, keep the fields detection cannot
   see, show and apply only differences, each with agreement; no difference: say so and
   stop. Both a shared and a personal file: update the shared one. `JOURNAL key` reports
   an invalid `Ticket pattern`: agree a fix with the user, proved with `--pattern`.
2. **Detect**, noting each value's source: forge and CLI login (`gh`, `glab`), default
   branch, tracker, test, lint and run commands (prefer what CI runs), links to agent
   instructions, tool configs and PR templates. Propose only commands a file names;
   when none does, omit the field and do not ask. No `origin`: the forge becomes one of
   the step 3 questions.
   Ticket key: one shell loop over
   `git for-each-ref --sort=-committerdate --count=50 --format='%(refname:lstrip=2)' refs/heads refs/remotes`
   (skip `*/HEAD`, strip `origin/`) prints each branch with the `key=` line of
   `JOURNAL key --branch "$b"`. Mostly numbers: no `Ticket pattern`. One shared prefix
   followed by digits (`ABC-123`): propose `ABC-\d+`, checked with `--pattern` on two branches. Several:
   ask in step 3. `Ticket branch`: the format seen, else `{id}-{slug}`.
3. **Ask**, in one message. The user may be meeting jam here, without its documentation.
   - Open with two or three sentences: jam takes a ticket from reading it to a PR
     (branch, tests, code, review), using a project file that lists this repository's
     commands; `init` writes that file and rules that make Claude ask before each push and
     each PR; it commits nothing.
   - Show the file from `project-template.md` (on update, only the differences), each
     line marked `detected (<source>)` or `to confirm`. The marks are shown, never
     written.
   - Ask three questions at most, with the question tool if available, recommended
     option first. Each question says in one sentence what it decides and why jam needs
     it. Each option says what it writes, where, and whom it affects. Use no jam
     vocabulary: describe effects.
     - Where the file lives: in the repository, committed, seen by everyone who clones
       (recommended when the user commits alone, else outside), or outside it, leaving the repository
       untouched. Permission rules mean "ask before each push and each PR"; outside the
       repository, they apply to all of the user's repositories.
     - What is sensitive here, from a short list drawn from the code (payments,
       authentication, personal data, migrations): a ticket touching it always gets one
       more review of its code by Claude before the PR.
     - Tracker, forge or ticket prefix, only if detection left it open.
   - Ask agreement to run the commands of step 4: list them, say why (a command is
     written only if it works) and that it may take minutes. Refused: every command is
     written unverified.
4. **Verify** from the toplevel, with a Bash timeout of 600000 ms, keeping only the exit
   code and the last 20 lines of output:
   - tests and lint exit 0;
   - reading an open ticket (from the list, or one the user gives) prints its title;
   - the list command, with `--limit 5`, exits 0;
   - `JAM_PR=<latest merged PR> /bin/sh -c '<PR state command>'` prints `merged` once
     stripped and lowercased; no merged PR yet: unverified.

   Never run the run command, the PR command or `Stage command`; write
   `<!-- unverified: never run by init -->` above them. Fix a failing command with the
   user; one kept anyway gets `<!-- unverified: <reason> -->` above it.
5. **Confirm once, then write.** First check that the settings file is valid JSON; if
   not, write nothing and stop.
   - Shared: warn if the branch is not the default one (other worktrees will not see the
     file until merge), or if `git check-ignore` reports `.jam/project.md` or
     `.claude/settings.json` (then propose personal).
   - The project file, whole: shared at `.jam/project.md`; personal as `project.md` two
     levels above the `journal=` path of `JOURNAL key --key setup` (create the
     directory).
   - Merge into `.claude/settings.json` (shared) or `~/.claude/settings.json`
     (personal), under `permissions.ask`, without duplicates: `Bash(git push *)` and the
     PR command's prefix, such as `Bash(gh pr create *)`.
6. **Summarize**: what was written, what to commit, what is unverified; next step
   `/jam:ticket <id>`.

## Rules

- Fields the script reads are bold, like `PR state command` in the template:
  `` - **Ticket pattern**: `ABC-\d+` `` (under Tickets), `Stage command`.
- `Stage command` goes to the personal file only, and only on request. One found in a
  shared file: report it, never copy it.
- The project file stays short, links to other files by path and copies
  nothing from them. `Review: project checks` starts empty.
- Prose in the user's language; section titles and field names in English.
