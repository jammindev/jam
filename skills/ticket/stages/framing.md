# Stage: framing

Before any `/clear` or end of session, the journal is up to date: stage, `Resume here`
(one or two sentences a new session can act on), new decisions.

1. Read the ticket with the project file's `Read a ticket` command, with the id as the
   tracker writes it. No command: ask the user. A branch with no ticket behind it
   (`refactor/auth`): ask the user what it is for.
2. Read the code the ticket touches. Propose a size, `small` or `medium`, with one
   sentence of reason, and say whether it is sensitive: it is when it touches an area
   listed under `Sensitive` in the project file.
   - Sensitive: say that a sensitive ticket needs the medium flow, which does not exist
     yet in jam, and stop.
   - Medium: say that only the small flow exists yet. The user may run it as small, or
     stop.
3. Agree with the user on three lines: the goal, one done criterion, and the test that
   proves it. A product question the code cannot answer is asked as a short
   multiple-choice question, recommended answer first.
4. Create the journal:

   ```
   JOURNAL init --size small --sensitive no --title "<title>" --goal "<goal>" \
     --done-when "- [ ] <criterion> · proof: <test id>" --resume "<next action>"
   ```

   `--resume` is the next action, such as "Write the failing test of …". Then record, with
   `JOURNAL set --decision "…"`, the choice to run a medium ticket as small if made,
   and each product answer.
5. Run the project file's `Tests` once on the untouched branch. A failure is not this
   ticket's: record it with `JOURNAL set --log "…"`, and agree with the user how to go
   on (a `.env` or dependency missing from the new worktree, a red base branch).

Then move on, as the skill says.
