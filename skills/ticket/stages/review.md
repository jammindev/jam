# Stage: review

Before any `/clear` or end of session, the journal is up to date: stage, `Resume here`
(one or two sentences a new session can act on), new decisions.

1. Run the `reviewer` subagent once. Give it, and nothing else:
   - the goal and the done criterion, from the journal;
   - the diff to review: `git diff origin/<base>...HEAD`, with `<base>` the project
     file's `Base branch`;
   - the project file's `Review: project checks`, if any;
   - the paths under its `Links` that serve a review (agent instructions, a review grid).
2. Check each finding in the code before acting on it. A finding is blocking only if it
   describes a concrete failure scenario or breaks the done criterion. Fix the blocking
   ones, run the tests again, commit. A small ticket gets no second pass.
3. `JOURNAL set --log "review: <N> blocking, <M> other"`, once per reviewer run, a
   targeted second review included, in exactly that form: the ticket's stats count it.

Then move on, as the skill says.
