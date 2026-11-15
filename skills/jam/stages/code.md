# Stage: code

Every line shown to the user is in their language.

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

1. Write the test of the done criterion. Run it and check that it fails, for the reason
   the criterion gives. Then write the code until it passes. A medium ticket follows
   its `Plan`, one criterion at a time, test first; a criterion proved by a check at
   acceptance has no test to write. When the plan does not fit the code,
   stop, say what does not fit, and agree the change with the user:
   `JOURNAL set --plan "…"`, and a decision. Never force the plan through (a weakened
   test, a workaround).
2. Run the project file's `Tests` (in the background, then read the result) and `Lint`.
   A command missing from the project file: ask the user for it, and offer to add it
   there. A failure unrelated to the change: stop, show the end of the output, and agree
   a fix with the user.
3. Record each decision the code made on its own:
   `JOURNAL set --decision "Decided by the code: … (to settle)"`. The user settles them
   at acceptance.
4. Once a test passes, tick its criterion by rewriting the whole section:
   `JOURNAL set --done-when "- [x] <criterion> · proof: <test id>"`, one line per
   criterion.
5. Commit on the ticket branch, in the style of the repository's recent commits. The
   user's own settings may ask for their agreement first.

Then move on, as the skill says.
