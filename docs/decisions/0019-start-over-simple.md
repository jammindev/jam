# ADR 0019: start over, simple

- **Status**: accepted (maintainer's green light, 2026-11-11)
- **Date**: 2026-11-11
- **Supersedes**: ADR 0001 to 0018, removed from `main` and kept at the tag `kit`.

## Context

The method kit, jam's previous version, grew heavy by building itself with itself: seven
roles, a coordinator and a task orchestrator, hooks guarding each role, a process that
needed its own pruning, and review rounds counted in tens. Running it cost the maintainer more attention than the tickets it carried.

A lighter method, already used daily on other projects, covers what matters: a ticket goes
from framing to merge across several sessions, and nothing is lost when the conversation is
cleared. Its memory is a journal kept outside the conversation, not a pipeline of roles.

## Decision

- **Same repository, history kept.** The old kit is frozen by the tag `kit`, as the
  Electron app was by `app-electron`. The branch of the unfinished autonomous mode is
  abandoned. The tree is emptied, except `LICENSE` and the spec of the journal script;
  the earlier ADRs go too.
- **Scope of the first version**: two skills, `init` and `ticket`; two subagents,
  `implementer` and `reviewer`; one script, `skills/ticket/journal.py`, with its pytest
  suite and CI; one non-blocking `SessionStart` hook that
  prints the current ticket's resume block. Nothing else until it has been used.
- **Journals live outside the repository**, under `~/.jam/<repo-id>/`, so that every
  worktree of a repository sees the same journal and nothing about a ticket is committed.
  A project file is either committed (`.jam/project.md`, shared) or kept outside the
  repository (personal); a personal one may override a shared one field by field.
- **The script owns the format, the model owns the content.** Anything with one correct
  answer (ticket key, journal path, next stage, whether to clear first) is computed by the
  script. Its behaviour is fixed by [`docs/specs/journal.md`](../specs/journal.md).
- **Public and in English**: README, skills, code and docs from this ADR on. Journals are
  written in the user's language. The repository
  goes public only after a secret scan of its whole history.
- **Nothing useless.** Every rule, command or option answers a need of the specs or a
  friction met on a real ticket. No numeric ceiling on size: one was tried and made a
  skill drop rules it needed (amended 2026-11-11).
- **Code is written by agents**; the maintainer reviews and decides. Commits, pushes and
  merges wait for the maintainer's explicit agreement.

## Consequences

- (+) jam fits in a few files that one person can read in an evening.
- (+) A cleared or compacted session resumes from the journal, in any worktree.
- (−) The reasoning behind the earlier versions is no longer on `main`; it is at the
  tag `kit`.
- (−) No role isolation and no permission profiles per role: the review is a subagent of
  the session, not a separate session with its own guard rails.
- (−) Two sessions writing the same journal at the same time can lose one write.
