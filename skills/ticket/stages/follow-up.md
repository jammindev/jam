# Stage: follow-up

Before any `/clear` or end of session, the journal is up to date: stage, `Resume here`
(one or two sentences a new session can act on), new decisions.

- When resumed or asked: show the PR's checks with the forge CLI (`gh pr checks <PR>`,
  `glab ci status`). A failing check is fixed on the branch, then pushed.
- A human reviewer asks for a change: record it with `JOURNAL set --decision "<request> (to settle)"`, then
  `JOURNAL set --stage code` and read `code.md`. The flow comes back through review,
  acceptance and delivery, which then only pushes.
- The merge is the user's. Once merged: `JOURNAL close`, with one `--pending "…"` per
  thing still open outside the code. Use `--force` only when the user asks for it
  explicitly; a refused close shows its reason. Pass on to the user any `jam:` warning
  it prints (stats that could not be read, a failing `PR size command`). Then give the commands to run from the main session, and run none of them:

  ```
  git worktree remove <path>
  git branch -D <branch>
  ```

  `<path>` and `<branch>` are the journal's `Worktree` and `Branch`. `-D`, because a squash merge leaves the local branch unmerged in git's eyes.
