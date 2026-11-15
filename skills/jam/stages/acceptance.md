# Stage: acceptance

Every line shown to the user is in their language.

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

The green light before the pull request (a medium ticket's second). Show, in one message
of plain text, never inside a question tool's form (the text before a form can be
hidden), and wait for the user's answer as text:

- the goal, and the criteria with their proofs;
- the decisions the code made on its own, to settle;
- what the review found, what was fixed, what was left: from the reports in
  `reports=` (`JOURNAL key`);
- if the change is visible: at most three points for the user to check (five for a
  medium ticket), and how to see them (the project file's `Run` command, a page, a
  command). When the project file's `Links` names an acceptance procedure, follow it to
  prepare them;
- each criterion proved by a check at acceptance, with how to check it, beyond that
  limit. Once the user accepts, tick them with `JOURNAL set --done-when` (the whole
  list).

Record the answer with `JOURNAL stop`:

- accepted as is: `JOURNAL stop seen`, or `JOURNAL stop explained` after an explanation.
  That is the green light;
- something to change, or accepted with something to add:
  `JOURNAL stop corrected --note "<what changes>"`, then `JOURNAL set --stage code` and
  read `code.md`. The flow comes back here, with a new message and a new stop.

Each decision to settle gets one more line, since decisions are never rewritten:
`JOURNAL set --decision "Settled: <decision> → kept"` (or `→ changed: …`).

Once accepted, move on, as the skill says.
