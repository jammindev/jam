# Stage: review

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

1. `git status --porcelain` must print nothing: the code stage commits before review.
   Otherwise show the diff to the user: a change the code stage did not make (one left
   by an interrupted review, say) is restored with `git restore`, never committed;
   commit the rest with their agreement, or stop. Never review an uncommitted diff.
   Then run the `reviewer` subagent once, in the foreground, and wait
   for its answer: it may change and restore files to test them, so touch no file in
   the worktree and run nothing on it until it has answered. Give it, and nothing else:
   - the goal and the done criterion, from the journal;
   - the diff to review: `git diff origin/<base>...HEAD`, with `<base>` the project
     file's `Base branch`;
   - the project file's `Tests` command;
   - the project file's `Review: project checks`, if any;
   - the paths under its `Links` that serve a review (agent instructions, a review grid).
2. When it has answered or stopped, run `git status --porcelain`. Anything listed comes
   from the review (a mutation left behind, files the tests wrote): show it to the user,
   and restore tracked files with `git restore` once they agree.
3. Check each finding in the code before acting on it. A finding is blocking only if it
   describes a concrete failure scenario or breaks the done criterion. Fix the blocking
   ones, run the tests again, commit. A small ticket gets no second pass; any other
   pass goes through steps 1 and 2 again.
4. `JOURNAL set --log "review: <N> blocking, <M> other"`, once per reviewer run, a
   targeted second review included, in exactly that form: the ticket's stats count it.

Then move on, as the skill says.
