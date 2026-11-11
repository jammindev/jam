# Stage: code

Before any `/clear` or end of session, the journal is up to date: stage, `Resume here`
(one or two sentences a new session can act on), new decisions.

1. Write the test of the done criterion. Run it and check that it fails, for the reason
   the criterion gives. Then write the code until it passes.
2. Run the project file's `Tests` and `Lint`. A command missing from the project file:
   ask the user for it, and offer to add it there. A failure unrelated to the change: stop, show the end of the output, and
   agree a fix with the user.
3. Record each decision the code made on its own:
   `JOURNAL set --decision "Decided by the code: … (to settle)"`. The user settles them
   at acceptance.
4. Once the test passes, tick the criterion by rewriting the section:
   `JOURNAL set --done-when "- [x] <criterion> · proof: <test id>"`.
5. Commit on the ticket branch, in the style of the repository's recent commits. The
   user's own settings may ask for their agreement first.

Then move on, as the skill says.
