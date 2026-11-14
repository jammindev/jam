# Stage: review

Every line shown to the user is in their language.

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

Back here from acceptance or follow-up (the journal's `Log` has an `acceptance → code`
or `follow-up → code` line after its last `review:` line): the review is one targeted
pass, as in step 3, the finding being the change asked (the note of the last
acceptance stop, or the last decision "to settle"); a sensitive ticket's extra pass is
targeted on it too.

1. `git status --porcelain` must print nothing: the code stage commits before review.
   Otherwise show the diff to the user: a change the code stage did not make (one left
   by an interrupted review, say) is restored with `git restore`, never committed;
   commit the rest with their agreement, or stop. Never review an uncommitted diff. Then
   run the `reviewer` subagent once, in the foreground, and wait for its answer: it may
   change and restore files to test them, so touch no file in the worktree and run
   nothing on it until it has answered. Give it, and nothing else (no tracker command to
   run; a review grid by its path, its steps never copied in):
   - the ticket's text, as the project file's `Read a ticket` command prints it, or
     the journal's `Goal` when no ticket is behind the branch;
   - the goal and the done criteria, from the journal;
   - the diff to review: `git diff origin/<base>...HEAD`, with `<base>` the project
     file's `Base branch`;
   - the project file's `Tests` command;
   - the project file's `Review: project checks`, if any;
   - the paths under its `Links` that serve a review (agent instructions, a review
     grid).
2. When it has answered or stopped, run `git status --porcelain`. Anything listed comes
   from the review (a mutation left behind, files the tests wrote): show it to the user,
   and restore tracked files with `git restore` once they agree.
3. Check each finding in the code before acting on it. A finding is blocking only if it
   describes a concrete failure scenario or breaks a done criterion. Fix the blocking
   ones, run the tests again, commit. A blocking fix gets a targeted pass: steps 1 and
   2 again, with the same brief, except the finding and the fix's diff
   (`git diff <the last report's HEAD>..HEAD`) in place of the whole diff.
   Repeat while a fix is blocking, three reviewer runs at most; then the user decides.
   The other findings, fixed or not, get no second pass.
4. After each reviewer run:
   `JOURNAL set --log "review: <blocking> blocking, <other> other"`, in exactly that
   form (the ticket's stats count it), and save its answer as it came to
   `<reports>/review-<run>.md` (`reports=` from `JOURNAL key`; `<run>` follows the
   highest number already there), its first line `HEAD: <the commit it reviewed>`.
   Acceptance and follow-up read the findings there, after a `/clear`.
5. `Sensitive: yes` in the journal: once the loop has ended (nothing blocking, or the
   user decided), one more reviewer run, through steps 1 to 4, with the same brief and
   a focus on the areas listed under `Sensitive` that the diff touches: who can read or
   change what, what can be lost or exposed, what a migration does to existing rows.
   Its blocking fixes get targeted passes as in step 3, three runs at most for this
   pass.

Then move on, as the skill says.
