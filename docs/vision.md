# Vision

Status: draft · Written 2026-11-11, from the design session that restarted jam (ADR 0019).

## The problem

Coding agents make a developer very productive on one change. A real ticket is more than
one change: it spans days and several conversations, it needs product decisions, and its
code must be reviewed by someone who did not write it. A conversation forgets all of that
when it is cleared or compacted, and the frameworks that try to fix it tend to grow
heavier than the tickets they carry. jam's previous version did exactly that.

jam is the opposite bet: a small, written workflow for product builders, people who own
a product from the need to the release and build it with coding agents. It starts with
the ticket, run from reading it to the pull request, keeps its memory in a journal
outside the conversation, and asks the developer only for the decisions that are theirs.
From there it grows toward the rest of the product work: the level above the ticket,
bugs and support, specifications.

## Principles

1. **Generic first.** Any stack, any tracker (GitHub, GitLab, Jira, Linear…), any
   project. The workflow names no tool: it runs the commands of the project file. jam
   is built for Claude Code first, and kept open to other agent tools: the core is
   Markdown and a Python script; only the plumbing (subagents, hook, plugin variables,
   `/clear`) is Claude Code's.
2. **Installs on an existing project by itself.** `init` reads the repository, fills the
   project file (forge, tracker, branches, commands) and asks only what it cannot
   detect.
3. **One ticket, one branch, one session.** The work of a ticket happens in its own
   worktree and session, which keeps the ticket's journal; the main session only starts
   tickets and follows them, and keeps no journal.
4. **The journal is the only state.** Outside the repository, written through a script,
   never by hand. Any session resumes from it, after `/clear`, a compaction or a week.
5. **A script for anything with one right answer**: which ticket, where its journal is,
   which stage is next, whether to clear first. The model writes the content.
6. **The developer decides; agents do and check.** Product decisions are made with the
   developer during framing, as short multiple-choice questions. Decisions the code made
   on its own are listed for the developer to settle. Nothing leaves the machine (push,
   pull request) without the developer's agreement, and the merge is theirs.
7. **Whoever writes does not review.** Reviews are done by a fresh agent, with a clear
   stopping rule: no blocking finding, three rounds at most. And the session that wrote
   the code of a medium ticket clears its conversation before review and acceptance: it
   would judge the code by what it meant to do, not by the ticket.
8. **Tests come from the request**, before the code, each done criterion naming its test.
9. **Process in proportion.** The ticket's size, decided at the start, sets the amount
   of framing, review and acceptance.
10. **Spend effort where it matters**: subagents run on Opus, at `xhigh` effort where
    they must think (plan, review), at `medium` where they apply a plan (code); and a
    short context.
11. **Link, never copy.** The project's conventions stay in `CLAUDE.md`, tool configs
    and forge templates; jam points to them. A lesson that deserves to last is moved
    there, with the developer's agreement.
12. **Nothing useless.** Every rule answers a need of the specs or a friction met on a
    real ticket. Start small and grow from real use; nothing is built "for later".

## What makes jam different

Many tools can resume a conversation. jam aims at three things together:

1. **One level above the ticket.** A ticket rarely stands alone: it belongs to a larger
   subject, such as a milestone or a project in the tracker (billing, for instance), and
   a decision made in one ticket binds the others. A ticket session should start with
   the context of its subject and the decisions already made there, and add its own.
2. **Context handled on purpose**: what each agent receives, when the conversation is
   cleared, which model does what.
3. **Resuming by opening a session**: no re-explaining, no lost decision.

The first release covers the third and part of the second. The level above the ticket
comes as soon as real tickets of one subject need it, which should be soon, since tickets
are usually grouped in projects.

## The map

From the main session of a project, a developer can do four things:

| Branch | What it is | When |
|---|---|---|
| **Take a ticket** | frame, test, code, review, accept, open the pull request | first release |
| **Detect a bug, answer support** | investigate from the code and from past journals | later |
| **Specify a new feature** | turn a need into tickets, using the product rules already settled | later |
| **Discuss the project** | an ordinary conversation | no skill needed |

The main session starts with the project's context: `CLAUDE.md`, the list of skills, the
memory index. A ticket gets one session of its own, in its own worktree, and every
decision is written to its journal. Its path: open a worktree; frame and plan, with a
review loop; tests first, then the code; a code review by a fresh agent, sized to the
ticket; a check of the interface; the pull request; follow-up until the merge, then
the lessons learned. The README describes it stage by stage.

The product rules settled in tickets connect the branches: they become the material for
support answers and new specifications. Journals live on the developer's machine, so
these rules also travel through the pull requests and the tickets they are copied to.
The first release builds only the first branch, but its journals are written to serve
the others.

## Roadmap

| Step | Content | Done when |
|---|---|---|
| 1. Skeleton | journal script, `init`, `ticket`, the reviewer subagent, the hook, README, CI; sizes small and medium; then the repository goes public after a secret scan of its history | `init` fills the project file of a real repository without manual correction up to its first ticket, and a first small real ticket reaches its green light before the pull request |
| 2. Real tickets | three tickets on a real personal project: one small, two medium, one of them sensitive; frictions noted in the lessons; for each, how often the developer corrected, review rounds, token use per subagent | the three pull requests are merged and their lessons written |
| 3. Corrections | only what step 2 showed: the level above the ticket as soon as two tickets of one subject need it; the large size; whether plan and test plan stay merged, and whether code moves to an implementer subagent | every addition answers a friction seen in step 2 |
| 4. A team repository | installed in personal mode on a team repository with another forge and tracker; three tickets, next to the team's own tooling, without replacing it | installing needed changes to the project file only, none to the plugin |
| 5. The other branches | bug and support, specification, product rules drawn from the journals; then, if wanted, other agent tools | not before step 4 is passed |

## Not jam

- An application or a user interface of its own.
- Roles with their own rules, layers of orchestration between sessions, cards, relays.
- A place for the project's conventions: they live where the project already keeps them.

Not in the first release: guards written as hooks, such as one requiring proof of review
before delivery, or permission rules. jam asks in the conversation before a push
or a pull request; rules and guards come back only if a push ever leaves without the
developer's agreement.

## Open questions

- Whether plan and test plan stay one document for medium tickets (decided at step 3).
- Whether code is written by a subagent or by the ticket session itself (decided at
  step 3, from token use and how often the developer corrected).
- The three-round ceiling on review loops: a starting value, to tune on real tickets.
- A lighter mode by ticket weight: lower effort for the subagents of a small ticket
  (a review at `high` rather than `xhigh`), decided from the token use and correction
  rate measured at step 2.
- The most reliable way to read Jira and Linear tickets (step 4).
- The shape of the level above the ticket: what a subject holds (context, decisions),
  how a ticket knows its subject (the tracker's milestone or project is the natural key),
  when decisions move up to it.
