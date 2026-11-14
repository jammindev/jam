# Stage: framing, medium ticket

Every line shown to the user is in their language.

Before handing back to the user, the journal holds what changed in this turn: new
decisions, and `Resume here` (one or two sentences a new session can act on) when the
next step changed; nothing changed, nothing to write. After a `/clear` or a closed
window, no turn is left to do it.

`framing.md` has read the ticket, checked it is still worth doing, and agreed the size
with the user: medium. Resumed with a journal already there: never run `JOURNAL init` again;
run step 1, read the ticket again with `Read a ticket`, then go on from the step
`Resume here` names. At step 7, a `Stop at framing` line already `seen` or `explained`
means the green light was given: move on.

1. Start the project file's `Tests` on the untouched branch in the background: a base
   suite can outlast a foreground command.
2. Draft, without asking yet:
   - the goal (with no ticket behind the branch: what the user said it is for);
   - the done criteria, each naming the test that proves it;
   - what the ticket asks that this ticket leaves out, if anything;
   - the plan: the steps in order, the files they touch, the tests first.
3. Create the journal with the draft, `--sensitive yes` when the ticket touches an area
   listed under `Sensitive` in the project file. `--done-when` holds one line per
   criterion, each `- [ ] <criterion> · proof: <test id>`:

   ```
   JOURNAL init --size medium --sensitive <yes|no> --title "<title>" --goal "<goal>" \
     --done-when "<criteria>" --plan "<plan>" --resume "<step 4: the product questions>"
   ```

   Record each thing left out with `JOURNAL set --decision "…"`.
4. Ask the product questions the code cannot answer, each a short multiple-choice
   question, recommended answer first, with what each answer costs. Record each answer
   at once with `JOURNAL set --decision "…"`, and update the criteria or the plan with
   `JOURNAL set` when it changes them. The user agrees to the whole framing at step 7,
   once it has been reviewed.
5. Run the `framing-reviewer` subagent once, in the foreground, and give it, and nothing
   else:
   - the ticket's text, as `Read a ticket` printed it, or the journal's `Goal`;
   - the goal, the done criteria, the plan, and the decisions, from the journal;
   - the paths under the project file's `Links` that serve it (agent instructions,
     specs).
   Check each finding in the code before acting on it. A finding is blocking only if it
   shows a criterion no test can prove or whose test would pass without the change, a
   plan step the code contradicts, something the ticket asks that no criterion covers
   and no decision leaves out, or a product rule the plan decides that is not among the
   decisions. Fix the blocking ones with `JOURNAL set` (asking the user when a product
   rule changes), then run the reviewer again while a finding is blocking, three runs at
   most; then the user decides. After each run:
   `JOURNAL set --log "framing review: <blocking> blocking, <other> other"`.
6. Read the base tests' result; still running: wait for it. A failure is not this
   ticket's: record it with `JOURNAL set --log "…"`, and agree with the user how to go
   on (a `.env` or dependency missing from the new worktree, a red base branch).
7. The first green light. Show, in one message of plain text, never inside a question
   tool's form, and wait for the user's answer as text: the goal; the criteria and
   their tests; the product decisions and what is left out; the plan; what the framing
   review found and what changed; the base tests' result. Record the answer:
   - accepted: `JOURNAL stop seen`, or `JOURNAL stop explained` after an explanation.
     That is the go-ahead to write code;
   - something to change: `JOURNAL stop corrected --note "<what changes>"`, apply it
     with `JOURNAL set`, show the changed lines, and ask again; the framing reviewer
     does not run again.

Then move on, as the skill says.
