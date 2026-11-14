# Stage: follow-up

Every line shown to the user is in their language.

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

- On arriving here from delivery: watch the PR's checks in the background with the
  forge CLI (`gh pr checks <PR> --watch`, `glab ci status --live`), and tell the user
  their result when they finish; no check reported yet: try again a minute later. When
  resumed or asked: show the checks again. A failing check is fixed on the branch,
  pushed with the user's agreement, and watched again.
- A human reviewer asks for a change: record it with
  `JOURNAL set --decision "<request> (to settle)"`, then `JOURNAL set --stage code` and
  read `code.md`. The flow comes back through review, acceptance and delivery, which
  then only pushes.
- The merge is the user's. Once merged, and before closing, one pass on the journal;
  follow-up teaches things too (a red CI, a merge order changed):
  1. Tick each box of `Done when` whose proof holds now, with `JOURNAL set --done-when`
     (the whole list). A box that cannot be ticked: say so. If the user decides to
     close anyway, record why with `JOURNAL set --decision "…"`; at the close below,
     add `--force` and the box as a `--pending`.
  2. Record the decisions taken since delivery with `JOURNAL set --decision "…"`, and a
     red CI fixed with `JOURNAL set --log "…"`.
  3. **Lessons**, each with `JOURNAL set --lesson "…"`. Start from the lessons already
     in the journal, noted during the ticket, and add only what is missing:
     `set --lesson` cannot take one back. Ask two separate questions:
     - About the code or the project: a trap met on this ticket? One or two lessons,
       or none. One may be promoted, with the user's agreement, to `CLAUDE.md`, to the
       project file's `Review: project checks`, or to a linter rule.
     - About jam: an instruction that failed, had to be worked around, or served no
       purpose? Each lesson starts with `jam:`. None at all: write
       `jam: nothing to report`, so that a silent answer is told from a forgotten
       question. At close, the script copies them to `jam-lessons.md` in jam's home
       (`~/.jam` by default), where jam's maintainer reads them; removing a rule is as
       good an outcome as adding one. This question has no recommended answer.
  4. **What remains open** outside the code: review findings left aside (in the reports
     of `reports=`, `JOURNAL key`), decisions still "to settle", remarks out of the
     ticket's scope. In one question listing them, ask the user which become an issue
     now: draft each, show it, and once they agree create it with the CLI the project
     file's commands use (`gh issue create`, `glab issue create`; none: hand the draft
     to the user), then `JOURNAL set --log "issue <id>: <title>"`. The others become a
     `--pending` at the close.

  Then `JOURNAL close`, with one `--pending "…"` per item kept open. An archive is never
  edited, by hand or otherwise: what was forgotten is told to the user. Use `--force`
  only when the user asks for it explicitly; a refused close shows its reason. Pass on
  to the user any `jam:` warning it prints (stats that could not be read, a failing
  `PR size command`). Then ask the user, and once they agree, remove the worktree and
  the branch from this session, as its last action (say so: the session's folder
  disappears with it). Do it the way the project's own instructions say (`CLAUDE.md`,
  the project's memory); otherwise read `<main worktree>`, the first path of
  `git worktree list`, then run, in one command:

  ```
  git -C <main worktree> worktree remove <path> && git -C <main worktree> branch -D <branch>
  ```

  `<path>` and `<branch>` are the journal's `Worktree` and `Branch`. `-D`, because a
  squash merge leaves the local branch unmerged in git's eyes. `worktree remove`
  refuses when files are modified, or untracked and not ignored: show them, and add
  `--force` only once the user agrees. Ignored files (`.env`, dependencies) go with
  the worktree.
