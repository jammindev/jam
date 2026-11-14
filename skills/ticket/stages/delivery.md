# Stage: delivery

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

The journal already has a PR (`JOURNAL show`, field `PR`): skip step 2, push only.

1. Ask the user, then push: `git push -u origin <branch>`.
2. Ask the user, then open the PR with the project file's `Open a PR` command, adding a
   title and a body: `--title "…" --body-file -` with the body on stdin for `gh`,
   `--title "…" --description "…"` for `glab`. Never write the body to a file inside the
   repository. The body follows the PR template under the project file's `Links` if
   there is one, and holds the goal, the criterion and its test, the product decisions,
   and `Closes #<id>` when the tracker is the forge's: the journal stays on this machine,
   the PR is where others see the decisions. Then `JOURNAL set --pr <number>`, the bare
   number read from the command's output.

Then move on, as the skill says.
