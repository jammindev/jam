# Stage: start (main session)

This session writes no journal: it creates the ticket's branch and worktree, then hands
over to a new session there.

1. Read the ticket with the project file's `Read a ticket` command, `{id}` replaced by
   the id. No such command: ask the user for the ticket's title and content.
   **Still worth doing?** Before anything else, check, reading only and on this ticket
   only:
   - already done: a merged PR names it, or the code already does what it asks (for a
     bug, read the function it blames);
   - blocked: it depends on a ticket still open (a "blocked by" line, a link);
   - outdated: the code it names is gone, or a later ticket or decision replaced it.
   Nothing points to done, blocked or outdated: say so in one line and go on. Any sign
   of one, proven or only suspected: give it in one to three lines with what shows it,
   and ask the user whether to go on; stop if they say no. Write nothing to the
   tracker.
   **Already started?** Look for work on this ticket, whatever created it: a branch
   whose `JOURNAL key --branch <name>` gives this key (`git branch -a`), or a worktree
   on such a branch (`git worktree list`). Found: create nothing, say so, and give the
   command to open a session in that worktree (or create the worktree for that branch,
   as in step 4). Two sessions may start the same ticket a few minutes apart.
2. Build the branch name from `Ticket branch`:
   - `{id}`: the ticket's id, without `#`;
   - `{slug}`: a few words of the title, lowercase ASCII, joined by `-`;
   - `{type}`, when the format has it: the kind of change (`feat`, `fix`…), among those
     seen in the repository's branches (`git branch -a`).
   Propose the name to the user and wait for their answer.
3. Run `JOURNAL key --branch <name>` (never with `--key`, which would win). Its `key=`
   must equal the ticket's key from the router. If not (a tracker key such as `ENG-142`
   with no `Ticket pattern`, typically), say so and propose either `/jam:init` again to
   add the pattern, or a branch named after the key itself.
4. The project's own instructions (`CLAUDE.md`, the project's memory) say how to create
   a worktree or open a session, with a tool of theirs: follow them for steps 4 and 5,
   with this branch name and the project file's `Base branch`, then say which way was
   used. Otherwise:
   run `git fetch origin`, then create the worktree next to this session's, at
   `<worktree>-<key>` lowercased (`<worktree>`: the `worktree=` of `JOURNAL key`), from
   the project file's `Base branch`:
   - new branch: `git worktree add --no-track -b <branch> <path> origin/<base>`;
   - a local branch with that name exists: `git worktree add <path> <branch>`;
   - only `origin` has it: `git worktree add -b <branch> <path> origin/<branch>`;
   - `git worktree list` shows it checked out already: reuse that path.
5. Give the command that opens the ticket's session and starts framing:

   ```
   cd <path> && claude "/jam:ticket"
   ```

   No id is needed there: the session finds the ticket from its branch. The same
   `/jam:ticket` resumes the ticket later.

   Add that jam must be enabled for that folder too: installed in user scope, or in
   project scope with `.claude/settings.json` committed on the base branch; local scope
   does not reach a new worktree. Write nothing else.
