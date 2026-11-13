# Stage: delivery

Before any `/clear` or end of session, the journal is up to date: stage, `Resume here`
(one or two sentences a new session can act on), new decisions.

The journal already has a PR (`JOURNAL show`, field `PR`): skip steps 1 and 3, push only.

1. **Lessons**, each with `JOURNAL set --lesson "…"`. Ask two separate questions:
   - About the code or the project: a trap met on this ticket? One or two lessons, or
     none. One may be promoted, with the user's agreement, to `CLAUDE.md`, to the
     project file's `Review: project checks`, or to a linter rule.
   - About jam: an instruction that failed, had to be worked around, or served no
     purpose? Start from the `jam:` lessons already in the journal and add what is
     missing, each starting with `jam:`. None at all: write `jam: nothing to report`, so
     that a silent answer is told from a forgotten question. These stay in the journal:
     jam's maintainer reads them, and removing a rule is as good an outcome as adding
     one.
2. Ask the user, then push: `git push -u origin <branch>`.
3. Ask the user, then open the PR with the project file's `Open a PR` command, adding a
   title and a body: `--title "…" --body-file -` with the body on stdin for `gh`,
   `--title "…" --description "…"` for `glab`. Never write the body to a file inside the
   repository. The body follows the PR template under the project file's `Links` if
   there is one, and holds the goal, the criterion and its test, the product decisions,
   and `Closes #<id>` when the tracker is the forge's: the journal stays on this machine,
   the PR is where others see the decisions. Then `JOURNAL set --pr <number>`, the bare
   number read from the command's output.

Then move on, as the skill says.
