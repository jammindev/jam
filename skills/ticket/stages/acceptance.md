# Stage: acceptance

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

The single green light of a small ticket. Show, in one message:

- the goal, and the criterion with its test;
- the decisions the code made on its own, to settle;
- what the review found, what was fixed, what was left;
- if the change is visible: at most three points for the user to check, and how to see
  them (the project file's `Run` command, a page, a command).

Record the answer with `JOURNAL stop`:

- accepted as is: `JOURNAL stop seen`, or `JOURNAL stop explained` after an explanation.
  That is the green light;
- something to change: `JOURNAL stop corrected --note "<what changes>"`, then
  `JOURNAL set --stage code` and read `code.md`. The flow comes back here, with a new
  message and a new stop.

Each decision to settle gets one more line, since decisions are never rewritten:
`JOURNAL set --decision "Settled: <decision> → kept"` (or `→ changed: …`).

Once accepted, move on, as the skill says.
