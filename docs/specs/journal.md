# Spec: `journal.py`, the ticket journal

Status: accepted (maintainer's green light, 2026-11-11) · Target: first release, step 1 (skeleton)

## Why

An agent's conversation forgets: `/clear` empties it, compaction summarizes it. A ticket
lasts days and spans several sessions, sometimes several worktrees. The journal is the
ticket's memory outside the conversation: goal, plan, decisions, and what to do next.

Anything that has exactly one correct answer is computed by the script: which ticket
this is, where its journal lives, which stage follows, whether to clear the conversation
first. The model writes the content; the script owns the format.

## Constraints

- One file, `skills/ticket/journal.py`. Python 3.9+, standard library only.
- Nothing useless: every command and option answers a need of this spec or of a skill.
- Nobody edits a journal by hand, the model included. Every change goes through a command.
- Writes are atomic: a temporary file in the same directory, then `os.replace`.
- Files are read and written as UTF-8, explicitly.
- Every `git` call has a 3 s timeout. The only commands that may reach the network are
  the ones the project file declares (see below).
- A refused write prints its reason on stderr, says that nothing was written, and exits 1.
  Read-only commands (`key`, `show`, `next`, `list`, `stats`) print the reason and exit 1.
  Usage errors keep argparse's exit code 2.
- Limitation, stated in the README: two sessions writing the same journal at the same time
  can lose one write. Atomic writes prevent a truncated file, not a lost update.

## Vocabulary

- **Ticket**: the unit of work, usually an issue in the tracker. Its **key** names its journal.
- **Stage**: where the ticket stands (table below).
- **Stop**: a moment where the session waits for the user, either a green light or a
  request to run `/clear`. The user's answer is recorded with `stop`.
- **Project file**: Markdown file describing the project for the model and the script.

## Where things live

```
$JAM_HOME (default ~/.jam)/
  jam-lessons.md          lessons about jam itself, gathered from every closed journal
  <repo-id>/
    project.md            personal project file (optional)
    journals/<KEY>.md     one active journal per ticket
    reports/<KEY>/        review reports, written by the skill, not by the script
                          (the small ticket writes none; kept for the medium one)
    archive/<KEY>.md      closed journals
```

`stats` also reads, and never writes, Claude Code's transcripts:
`$CLAUDE_CONFIG_DIR/projects/` when that variable is set, else `~/.claude/projects/`.

### repo-id

It must be identical from the main worktree and from every linked worktree. Two distinct
repositories get distinct ids in practice; rare collisions are accepted (`acme/shop-x`
and `acme-shop/x` share `acme-shop-x`, and the host is not part of the id).

1. If `origin` exists: take `git remote get-url origin`, remove the scheme, the user, the
   host and the port, and a trailing `.git`. Keep the whole remaining path, so GitLab
   subgroups stay distinct. Join its segments with `-`, lowercase.
   - `git@github.com:Acme/Shop.git` → `acme-shop`
   - `https://github.com/acme/shop` → `acme-shop`
   - `ssh://git@gitlab.example.com:2222/group/sub/app.git` → `group-sub-app`
   - A local path as remote (`/srv/git/app.git`) → its path segments, same rule.
2. Without `origin`: the main worktree's directory name, lowercased, then `-` and the first
   6 hex characters of the SHA-1 of the absolute path of `git rev-parse --git-common-dir`.
   The main worktree is the parent of that directory; for a bare repository, the directory
   itself. Ask git for an absolute path (`--path-format=absolute`, git 2.31+).
3. Sanitize: characters outside `[a-z0-9_.-]` become `-`, repeated `-` collapse, leading
   and trailing `-` and `.` are removed. An empty result is an error.

### Project files

Two may exist, and both are read:

- the shared one, `<toplevel>/.jam/project.md`, committed with the repository;
- the personal one, `$JAM_HOME/<repo-id>/project.md`, never committed.

The personal file overrides the shared one field by field. A project file that is only
git-ignored inside the repository is not supported: it would exist in one worktree only.

## Fields the script reads

Written as `- **Field**: value`. A pair of backticks around the whole value is removed.
Everything else in the file is for the model.

| Field | Where it may be set | Example |
|---|---|---|
| `Ticket pattern` | shared or personal | `ABC-\d+` |
| `PR state command` | shared or personal | `gh pr view "$JAM_PR" --json state --jq .state` |
| `PR size command` | shared or personal | `gh pr view "$JAM_PR" --json additions,deletions,changedFiles --jq '"\(.additions) \(.deletions) \(.changedFiles)"'` |
| `Stage command` | **personal only** | `tmux rename-window -t "$TMUX_PANE" "$JAM_KEY $JAM_STAGE"` |

`PR size command` must print three integers: lines added, lines removed, files changed.

### Trust

A project file is code, like a Makefile. The skill runs the commands it lists (tests,
opening a PR), the script runs `PR state command` on `close` and `PR size command`
whenever stats are computed (`close`, `stats`), and the session-start hook evaluates
`Ticket pattern`. The README says so plainly: do not run jam on a branch whose
project file you do not trust, exactly as you would not run its `make test`.

One field gets a stricter rule. `Stage command` runs on every stage change, without any
command being visible in the conversation, so it is read from the personal file only. A
shared file that sets it is ignored, with a warning on stderr.

An invalid `Ticket pattern` (`re.error`) is reported by every command except `resume`,
which stays silent. A pathological pattern can still hang the regex engine: the hook
entry carries a 5 s timeout so that a session start is never blocked longer.

### How commands run

- Through `/bin/sh -c`, with the working directory set to the toplevel of the worktree
  given by `--cwd` (or the current one).
- Values reach the command **only as environment variables**, never interpolated into the
  command string:
  - `JAM_KEY`, `JAM_STAGE`, `JAM_REPO`;
  - `JAM_PR`: the PR value, empty when `(none)`;
  - `JAM_WORKTREE`: empty when `(none)`;
  - `JAM_RESUME`: the first line of `Resume here`, not truncated.
- Timeouts: 5 s for `Stage command`, 20 s for `PR state command` and `PR size command`.

## Ticket key

Every key is uppercased, so that `abc-12` and `ABC-12` can never become two files on a
case-sensitive filesystem and one on macOS.

1. `--key <value>`: sanitized, uppercased.
2. The project file's `Ticket pattern`, used as written (the script adds no anchor) and
   searched case-insensitively in the branch name. If the pattern has a capturing group,
   the key is group 1; otherwise the whole match. A declared pattern replaces the default
   one: when it does not match, go to step 4.
3. Without a pattern, the default: a number at the start of the branch or right after a
   `/`, followed by `-` or the end: `(?:^|/)(\d+)(?=-|$)`.
   - `142-export-stock` and `feat/142-export` → `142`
   - `fix-2026-dates` → no match (a number in the middle is never a key)
   - `feat/abc-12-x` → no match: prefixed keys need a declared pattern, which `init`
     proposes when it detects them in the branch names.
4. No match: the sanitized branch name. `refactor/auth` → `REFACTOR-AUTH`.
5. Detached HEAD without `--key`, or not inside a git repository: error.

Every result, whatever the step, is sanitized then uppercased. Sanitizing: characters
outside `[A-Za-z0-9_.-]` become `-`, repeated `-` collapse, leading and trailing `-` and
`.` are removed. An empty result is an error. A key can therefore never contain `/` or
start with `.`.

## Stages

Declared once, as data. Adding a stage must only change this table.

| Stage | Clear the conversation first |
|---|---|
| `framing` | no |
| `code` | no |
| `review` | yes |
| `acceptance` | yes |
| `delivery` | no |
| `follow-up` | no |
| `closed` | only reachable with `close` |

Review and acceptance start from an empty conversation because the session that wrote
the code judges it by what it meant to do; a new session can only judge it by the ticket.

For a ticket of `Size: small`, `next` always answers `clear_first=no`: the small-ticket
flow has no clear.

## Journal format

Content follows the user's language. Field names and section titles are fixed, in English,
because the script parses them. Sections always appear in this order.

```markdown
# 142 · Export the month's stock movements as CSV

- **Stage**: review
- **Size**: medium
- **Sensitive**: no
- **Branch**: 142-export-stock
- **Worktree**: /home/dev/work/shop-142
- **PR**: (none)
- **Updated**: 2026-11-12 21:10

## Goal
The warehouse manager downloads the month's stock movements to check them.

## Done when
- [x] The file has date, product, quantity, reason · proof: tests/test_export.py::test_columns
- [x] A cancelled movement does not appear · proof: tests/test_export.py::test_cancelled

## Plan
1. Export view  2. Filter out cancelled movements  3. Button on the stock page

## Decisions
- Stop at framing (green light): corrected, leave cancelled movements out
- Semicolon separator: the file opens in French-locale Excel.
- Each line keeps the movement's reason as entered.
- Decided by the code: an empty month gives a header-only file (to settle)

## Resume here
Run the code review on the branch, then check each finding in the code before fixing.

## Lessons

## Log
- 2026-11-11 20:40 · created at framing
- 2026-11-11 21:30 · framing review, round 1: 1 blocking, 2 suggestions
- 2026-11-11 21:50 · stop at framing: corrected
- 2026-11-11 21:55 · framing → code (+2 decisions)
- 2026-11-12 21:10 · code → review (+1 decision)
```

- The first line is `# <KEY> · <title>`.
- `Updated` and log timestamps are local time, `YYYY-MM-DD HH:MM`.
- `Decisions` and `Log` are chronological: new lines are appended.
- `Size` is `small` or `medium`; `large` comes with its workflow. `Sensitive` is `yes` or `no`.
- The parser recognizes only the section titles above, plus `## Stats`, as `## Title` at
  the start of a line. Anything else is content.
- `## Stats` exists only in archived journals: `close` writes it between `Lessons` and
  `Log` (see `stats`), replacing it if a previous close wrote one before failing. It is
  never rendered empty, and a journal without it is valid.
- `Branch`, `Worktree` and `PR` hold `(none)` when unknown.
- A ticked box in `Done when` means its test passes, nothing more.

## Input rules

They apply to every command that writes, and are checked before anything is written.

- **One-line values** (`--title`, `--decision`, `--lesson`, `--log`, `--pending`,
  `--note`, `--about`, `--pr`): any run of whitespace, line breaks included, becomes one space.
- **Multi-line values** (`--goal`, `--done-when`, `--plan`, `--resume`): line breaks are
  kept; a line whose first non-space character is `#` is refused, because it could read
  as a section.
- **A decision that imitates a stop line** is refused, and the message gives the `stop`
  command. Imitation means matching, case-insensitively,
  `^stop at \S+.*:\s*(seen|corrected|explained)\b`. "Stop the cron before migrating" is
  an ordinary decision.
- `--about` containing `(` or `)` is refused, since the written stop line uses
  parentheses around it.

## Commands

Every command accepts `--key` and `--cwd`.

### `key`

Prints, one per line: `key=`, `branch=`, `worktree=`, `main_worktree=yes|no` (`yes` when
the checkout is the repository's main worktree, its git dir being the common git dir),
`repo=`, `journal=`, `exists=yes|no`, `archived=yes|no`, `project_files=` (paths
separated by `:`, empty when none), `reports=`. A missing value is printed empty. Writes nothing.

Two options let `init` prove a `Ticket pattern` before writing it:

- `--branch <name>`: resolve the key as if `<name>` were the current branch, which
  `branch=` then prints;
- `--pattern <regex>`: use this pattern instead of the project files' `Ticket pattern`,
  even when theirs is invalid. An invalid `--pattern` is an error.

`--key` still wins over both.

### `init`

Required: `--title`, `--goal`, `--done-when`, `--resume`. Optional: `--plan`,
`--size` (default `medium`), `--sensitive` (default `no`), `--force`.

Creates the journal at `framing`, with the log line `created at framing`.

- An archived journal exists for the key: refused, even with `--force`. The message gives
  the archive's path. Reopening is out of scope.
- An active journal exists: refused, unless `--force`.
- No `--key` and the branch is the repository's default branch (from
  `git symbolic-ref refs/remotes/origin/HEAD`, else `main` or `master`): refused. A ticket
  journal on the default branch would show up in every session of the main worktree.
- `Branch` and `Worktree` are filled from the checkout given by `--cwd` (or the current
  one) only when that checkout resolves to the same key; otherwise they stay `(none)`.
  The ticket session runs `init` from its own worktree, which keeps the journal there.

### `show`

Prints the whole journal. No journal: error.

### `set`

Options: `--stage`, `--title`, `--goal`, `--done-when`, `--plan`, `--resume`, `--pr`,
`--size`, `--sensitive`, and the repeatable `--decision`, `--lesson`, `--log`.

- `set` with no option is refused.
- `--stage`, `--size` and `--sensitive` use argparse choices: an invalid value is a usage
  error (exit 2). `closed` is not among the stage choices.
- Going back is allowed (`review` → `code`). Passing the current stage is not a stage
  change: no arrow in the log, no `Stage command` for it; the other options of the same
  call still apply.
- `Branch` and `Worktree` are refreshed only when the checkout given by `--cwd` (or the
  current one) resolves to the same key. This keeps a call from the main worktree, with
  `--key`, from recording the default branch as the ticket's branch.
- `Updated` is set on every write.

**Log line**: one per `set`, made of these parts in this order, joined by ` · `, each
only when it applies:

1. `<old> → <new>` on a stage change, followed by ` (+N decisions)` when decisions were added;
2. `+N decisions` when decisions were added without a stage change;
3. `PR <value>`;
4. each `--log` text.

In both forms, N = 1 is written `+1 decision`. Stop lines, added by `stop`, are not
counted here.

A `set` that only changes other fields (title, goal, plan, resume, size, sensitive,
lessons) writes no log line.

### `stop <seen|corrected|explained>`

Options: `--about` and `--note`. The stage is read from the journal.

- `seen`: the user accepted as is. `corrected`: the user changed something; `--note` is
  required. `explained`: the user asked for an explanation, then accepted.
- The line `Stop at <stage>` + ` (<about>)` if given + `: <verdict>` + `, <note>` if
  given is appended to `Decisions`.
- Log line: `stop at <stage>: <verdict>`.
- The share of `corrected` among all stop lines of `Decisions` measures how often the user
  had to rework the agent's output. The format must stay parseable for that count.

### `next`

Prints `current=`, `next=`, `clear_first=yes|no`. At `follow-up`, prints `next=closed`
and `hint=run close once the PR is merged`.

### `resume`

The block injected by the session-start hook. Built in memory, printed in one write.

Content, in order: the title line; stage, size and PR if any; the first line of `Goal`;
the last three decisions that are not routine stops; `Resume here`; the journal's path
with a reminder to update the journal before any `/clear`.

- A routine stop is a `seen` or `explained` stop without a note. A `corrected` stop is
  always kept.
- At most 30 lines: if `Resume here` would exceed it, it is cut and ends with `…`.
- No journal for the current key: prints nothing, exit 0.
- **Never fails.** Any exception, a missing git included, ends silently with exit 0.

### `list`

Active journals of the current repository: a header line, then one row per journal with
key, stage, PR and last update, aligned in columns. No journal: prints `no journal`.
Outside a git repository: error.

### `close`

Options: the repeatable `--pending` (what remains open outside the code) and `--force`.

Checks, in this order, before anything is written:

1. No archive may exist for the key.
2. Without `--force`: the journal has a PR, a `PR state command` is set, and its output,
   stripped and lowercased, is `merged`. A command that fails or times out refuses the
   close and says so.

Then, in this order: the stage becomes `closed`; `Resume here` becomes
`Closed on YYYY-MM-DD.` followed by one `- <item>` line per pending item; the log line
`closed · N pending` (or `closed (forced) · N pending`) is added; the `## Stats` section
is written (see `stats`; reading the transcripts can never refuse or fail a close: on any
error the section keeps the figures that come from the journal, says why the others are
missing, and the problem is reported as `stats` describes); the journal is written
and moved to `archive/`; its lessons starting with `jam:` (case-insensitive) are appended
to `$JAM_HOME/jam-lessons.md`, one line each:
`- YYYY-MM-DD · <repo-id>#<KEY> · <lesson>` (the closing day; `jam: nothing to report` is
not copied); `Stage command` runs. Lessons about jam
belong to jam, not to the project: the journal keeps their context, this file gathers
them across every repository for jam's maintainer. A failure to write it is reported on
stderr and changes neither the exit code nor the archive. Worktree removal is not the script's job: it prints the path, and the session asks the
user before removing anything.

### `stats`

Accepted (maintainer's green light, 2026-11-13).

Prints the ticket's figures in the exact form `close` writes into `## Stats`. Read-only.
No journal: error. On an archived journal that has a `## Stats` section, prints that
section as written: Claude Code deletes old transcripts (after 30 days by default), so the
figures recorded at close are the ones that last. Otherwise it computes them.

**Why.** jam claims a method; its cost and its weak points should be measured, not
guessed. Each figure answers one question:

| Figure | Question | Source |
|---|---|---|
| Elapsed | How long did the ticket take, start to finish? | journal, transcripts |
| Agent time | How much of that did agents actually work? | transcripts |
| User prompts, answers | How often did the user have to step in? | transcripts |
| Corrected stops | How often did the user rework the agent's output? | journal |
| Reviews | Is the reviewer worth what it costs? | both |
| Tokens per agent and model | What did each agent consume? | transcripts |
| Diff | Was the ticket costly because it was big, or because the work went badly? | PR |
| Context | Do sessions saturate their context? | transcripts |

No figure in dollars: Claude Code's own cost record is missing from some transcripts and
resets when a session is resumed, and a price table in the script would go stale and mean
nothing on a subscription. Tokens are the honest unit.

**Output.** Fixed format, parseable for a later aggregation across tickets. The figures
were measured on a real ticket:

```markdown
## Stats
- **Elapsed**: 6 h 32 (2026-11-13 15:29 → 2026-11-13 22:01)
- **Agent time**: 34 min
- **User**: 7 prompts, 3 answers · stops: 0 corrected of 1
- **Reviews**: 1 run, 1 logged · 1 blocking, 6 other
- **Tokens** (out · in · cache write · cache read):
  - main · claude-opus-5-5: 33.4k · 190 · 217k · 8.6M
  - jam:reviewer ×1 · claude-opus-5-5: 44.7k · 58 · 111k · 2.0M
- **Diff**: +62 −1 · 3 files
- **Context**: 0 compactions, 0 clears
- **Source**: Claude Code 2.1.296 transcripts, read 2026-11-13 22:01 (local time)
```

When the transcripts cannot be used, every figure that depends on them reads
`unavailable (<reason>)` or `suspect (<reason>)` (see below), and the journal's figures
stay. `Source` reads `none` when they are unavailable; when they are suspect it keeps
its usual form, since the version is what tells which update moved the format:

```markdown
## Stats
- **Elapsed**: 6 h 26 (2026-11-13 15:35 → 2026-11-13 22:01)
- **Agent time**: unavailable (no transcript)
- **User**: prompts unavailable (no transcript) · stops: 0 corrected of 1
- **Reviews**: runs unavailable (no transcript), 1 logged · 1 blocking, 6 other
- **Tokens**: unavailable (no transcript)
- **Diff**: +62 −1 · 3 files
- **Context**: unavailable (no transcript)
- **Source**: none
```

- Durations are rounded half up to the minute, then written `N min` under an hour,
  `H h MM` from an hour, `D d H h` from a day.
- Token counts: plain under 1 000, then `k` with one decimal under 100 k and none above,
  then `M` with one decimal, rounding half up. The unit is chosen after rounding: 999 600 is `1.0M`.
- **Elapsed** starts at the earlier of the first counted entry that is not neutral (see
  below) and the `created at framing` log line (framing happens before `init`), and ends
  at the last `closed` log line, or now for an active journal. Both ends are truncated to
  the minute, as displayed, before subtracting. It includes the wait between the merge
  and the close. With neither a creation line nor a counted entry, it reads
  `unavailable (no creation line)`.
- **Corrected stops**: the stop lines of `Decisions`, as in `stop`.
- **Findings**: the sum of the `review: <N> blocking, <M> other` log entries the review
  stage writes. Each log line is split on ` · ` and each part is read on its own (a
  `--log` passed with `--stage` follows the arrow). The model often adds details in
  parentheses: every innermost group, with the spaces before it (`\s*\([^()]*\)`), is
  removed repeatedly until none remain, then the part must start with
  `review: (\d+) blocking, (\d+) other\b`; a part that does not is left out of the sum.
- **Reviews**: `runs` is the number of counted subagents of type `jam:reviewer`, `logged`
  the number of parts that match. They differ when a review was not logged in the
  `review:` form (a targeted second review logged as free text, say); showing both keeps
  the findings honest. The review stage logs every run in that form.
- **Diff**: the output of `PR size command`, written `+A −D · F files` (`1 file` for one).
  It comes from the PR because, once the branch is merged, `git` can no longer tell the
  ticket's diff reliably (a merge commit makes the branch part of the base, a squash
  leaves no branch history). The output is stripped, then split on whitespace; it must
  give three integers. Otherwise `unavailable (<reason>)`, the reason being one of
  `no PR`, `no PR size command`, `PR size command failed`, `PR size command timed out`,
  `unexpected output`. It does not depend on the transcripts and is not a sanity check.
  At `close`, the last three reasons are reported on stderr (a wrong command shows on the
  first ticket, as `init` promises), never in `jam-lessons.md`: the project file is at
  fault, not jam. A failure never refuses the close.
- **Context**: compactions are the counted `system` entries of subtype
  `compact_boundary`, with `(N automatic)` added when some have
  `compactMetadata.trigger` `auto`; clears are the counted user entries whose text starts
  with `<command-name>/clear</command-name>` (Claude Code writes it at the start of the
  new session). Main sessions and subagents alike. `1 compaction`, `1 clear` in the
  singular. The review and acceptance stages of a medium ticket clear by design: the
  figure is read against the ticket's size.

**Which transcripts belong to the ticket.** A ticket session always runs in the
ticket's own linked worktree (the ticket skill stops otherwise), so the worktree
identifies them; nothing has to be recorded when a session starts, and the session-start
hook stays read-only.

1. Requires a `Worktree` in the journal; `(none)` gives `unavailable (no worktree)`.
2. Claude Code names a project directory after the session's working directory, every
   character outside `[A-Za-z0-9]` replaced by `-`. The candidate is the directory under
   the transcripts root with that name for the resolved (`realpath`) worktree path. This
   naming is Claude Code's, observed and not documented; no directory gives
   `unavailable (no transcript)`.
3. Every `*.jsonl` file of that directory is a main session. A session belongs to the
   ticket when its earliest entry that has a `cwd` (by timestamp) is the worktree or
   inside it, both paths resolved: a session that later moves into a scratch directory
   keeps all its entries. A session with an entry whose `entrypoint` is `sdk-cli` is
   left out: another program called Claude Code through its SDK (observed: a terminal
   app naming the chat), not a ticket session. A directory where no session belongs
   gives `unavailable (no session in the worktree)`.
4. Subagents of a session that belongs: `<session file without .jsonl>/subagents/agent-*.jsonl`,
   their type in the sibling `.meta.json` (`agentType`, else `unknown`). A subagent with
   no counted entry is not a run.
5. Only entries with a `timestamp` up to the bound are counted. The bound, for `close`,
   is the moment of the close; for an archived journal without `## Stats`, the start of
   the minute of its last `closed` log line, converted from local time to UTC with the
   machine's time zone (transcripts are in UTC); for an active journal, none. The start,
   not the end: the session usually asks right after the close whether to remove the
   worktree, and that exchange falls in the same minute. The price is the close's own
   turn, left out; this only concerns journals archived before `## Stats` existed.
6. A resumed or forked session is copied into a new file with the same entry `uuid`s:
   entries are counted once per `uuid`, subagents once per file name.
7. Lines that are not JSON, and fields that are missing or of the wrong type, are
   skipped silently. The transcript format belongs to Claude Code and changes without
   notice: the reading lives in one function, and an error in it degrades to
   `unavailable (unreadable transcripts: <error>)`, never to an exception.

**Reading an entry.** Each counted entry is one of:

- a **user prompt**, in a main session only (a subagent's first entry is its parent's
  request): `type` `user`, not `isMeta`, not `isCompactSummary`, `promptSource` not
  `system`, with text or image content and no `tool_result` block, the text not starting
  with `<task-notification>`, `<local-command`, `<command-name>`, `<command-message>`,
  `<bash-input>`, `<bash-stdout>`, `<bash-stderr>` or `[Request interrupted by user`
  (slash commands, shell escapes and the marker Claude Code writes when Escape stops the
  agent are not interventions; the message typed next is); or an `attachment` of type `queued_command` whose `origin.kind` is
  `human` (typed while the agent was working);
- a **user answer**: a `tool_result` for a `tool_use` named `AskUserQuestion` or
  `ExitPlanMode`, or one whose `permissionDecision.source` is `user_temporary` (the only
  value observed) or whose `toolUseResult` is `User rejected tool use`: the agent was
  waiting for the user;
- a **notification**: any other `user` entry without a `tool_result` block, except a
  compaction summary: a task notification, a message from another session or agent, a
  slash command, a shell escape, a usage-limit notice. They often arrive after hours of
  waiting, so they must end a wait;
- **work**: an `assistant` entry, or a `tool_result` that is not an answer;
- **neutral**: everything else (attachments, system entries, compaction summaries,
  metadata lines). Neutral entries are ignored entirely by agent time (the `Context` line
  still counts compaction boundaries): hook attachments are stamped
  a few milliseconds before the tool result they follow, and would otherwise cut every
  busy interval.

**Agent time.** Within each transcript, the non-neutral entries sorted by timestamp, each
gap between an entry and the next is a busy interval when the next one is work: the model
was answering or a foreground tool was running. A gap that ends in a prompt, an answer or
a notification is a wait; a tool running in the background is not counted. Agent time is
the length of the union of the busy intervals of every counted transcript, main sessions
and subagents together: a background reviewer working while the main session waits is
counted once.

**Tokens.** From the `message.usage` of counted `assistant` entries, grouped by agent
(`main`, or the subagent type with its number of runs) and by `message.model`: within a
group, `output_tokens`, `input_tokens`, `cache_creation_input_tokens`,
`cache_read_input_tokens`. A message written over several lines carries partial counts on
the first ones, so each field is the maximum seen for its `message.id`, across every
file. Messages whose model is `<synthetic>` (written by Claude Code, not by a model) are
left out. Claude Code's side calls (titles, summaries, and above all the summary a
compaction writes) do not appear in transcripts and are not counted: on a compacted
session, output tokens read a quarter to a half below Claude Code's own record.

**Version and sanity checks.** The `Source` line names the Claude Code versions found in
the counted entries' `version` field (`2.1.296`, or the lowest and highest compared
numerically, `2.1.9–2.1.10`), so that a figure that drifts in an aggregation can be
traced to an update. A format change rarely breaks
the reading outright; it makes figures silently wrong. So when at least one session
belongs to the ticket, each of these, checked across the whole ticket (an empty session
on its own is normal), makes the transcript figures `suspect (<reason>)` instead of
printing them as true: no `assistant` entry, no `usage`, no busy interval. (No user prompt is not one: a session launched with `/jam:ticket` and
driven by questions alone has none.)

**Reporting it.** At `close`, any `unavailable` or `suspect` of the transcript figures,
except `no worktree`, is reported on stderr, so the ticket session tells the user, and
appended to `$JAM_HOME/jam-lessons.md` like a lesson about jam:
`- YYYY-MM-DD · <repo-id>#<KEY> · jam: stats <reasons> (Claude Code <versions>)`, the
distinct reasons joined by `; `, each reason flattened to one line and cut to 200
characters, `version unknown`
when none was read. `no transcript` is reported too: the close itself runs in a ticket
session inside the worktree, so a missing transcript means the naming or the `cwd` field
changed. The line is written in the same step as the `jam:` lessons, after the archive is moved,
so a second close after a failed move does not write it twice. The maintainer learns of
a format change from the first ticket it touches.

## Stage command

After a successful `init`, `set` that changed the stage or `Resume here`, or `close`, the
script runs the personal `Stage command` if one is set and a worktree is recorded. Its
failure, its timeout or its output never change the exit code or the journal. This is how
an outside tool (a terminal title, a task board) can follow the ticket without the script
knowing it.

## Session-start hook

`hooks/hooks.json` in the plugin: event `SessionStart`, matcher
`startup|resume|clear|compact`, command
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/ticket/journal.py" resume`, `"timeout": 5`. It
blocks nothing and writes nothing.

## Out of scope for step 1

- A second track for reviewing someone else's PR, and closing on a PR closed without merge.
- Product validation as an interrupting stage, with a return to the interrupted stage.
- A review stamp (a fingerprint of the reviewed diff) and a delivery guard that checks it.
- Reopening an archived journal; decisions inherited from the ticket's subject (a
  milestone or tracker project, the level above the ticket; see `docs/vision.md`).
- Writing follow-ups anywhere else than the archived journal.
- Starting `init` at a later stage, or with a PR.
- Listing every repository at once.
- Repairing journals written by another version (missing sections or fields).
- Any write to the tracker. The skill does it with commands from the project file, with
  the user's agreement.
- Stats across tickets (per project, per stage, per size): once about ten journals are
  archived, from their `## Stats` sections. A figure joins only to answer a question.
- In `stats`: dollars; the `start` stage, run by the main session before the worktree
  exists; a session that moves into the worktree from elsewhere, or that starts in a
  subdirectory of it (Claude Code files it under another directory); worktree paths whose
  directory name Claude Code shortens (beyond 200 characters); other agents than Claude
  Code. A worktree path reused by an earlier ticket mixes both tickets' figures.

## Tests

`tests/test_journal.py`, pytest. Each test builds temporary git repositories (with a
linked worktree where needed) and points `JAM_HOME` to a temporary directory. CI runs the
suite on Python 3.9 and 3.13, with `ruff check`.

**Key and repo-id**

1. With the pattern `ABC-\d+`: `abc-123-filter` → `ABC-123`. With `(\d+)-`: `x/77-y` → `77`.
2. Default pattern: `142-export` → `142`; `feat/142-export` → `142`;
   `fix-2026-dates` → `FIX-2026-DATES`; `feat/abc-12-x` → `FEAT-ABC-12-X`;
   `refactor/auth` → `REFACTOR-AUTH`.
3. `--key abc-12` → `ABC-12`, whatever the branch.
4. Detached HEAD without `--key`, and a directory outside git: error.
5. repo-id: the https and ssh forms of one remote give the same id; ssh with a port; a
   GitLab subgroup keeps every segment; identical from a linked worktree.
6. Two repositories without remote and with the same directory name get two repo-ids; a
   repository without remote gets the same id from a linked worktree.
6b. `--key ..` and `--key .x` are refused or sanitized so that no path leaves `$JAM_HOME`;
    detached HEAD with `--key` works.
7. Two repositories with a ticket `142` never share a journal file.

**Project files**

8. The personal file overrides a field of the shared one.
9. A `Stage command` in the shared file is ignored, with a warning, and never runs.
9b. An invalid `Ticket pattern` makes `key` fail with a message and `resume` print nothing.
10. A value wrapped in backticks is read without them.

**Writing**

11. `init`: refused when a journal exists, overwritten with `--force`; refused when an
    archive exists, even with `--force`; refused on the default branch without `--key`;
    `Size` and `Sensitive` default to `medium` and `no`.
12. `init --key 142` from another checkout leaves `Branch` and `Worktree` at `(none)`.
13. `set --stage nope`, `set --stage closed`, `--size huge` and `--sensitive maybe` exit
    2; `set` with no option exits 1; in every case the file stays byte for byte unchanged.
14. A multi-line `--decision` is stored on one line. A `--goal`, `--plan`, `--done-when`
    or `--resume` with a `## ` line is refused.
15. `--decision "Stop at framing: seen"` is refused; `--decision "Stop the cron first"`
    is accepted.
16. `set --key 142` run from the main worktree leaves `Branch` and `Worktree` untouched.
17. Log lines: `framing → code (+2 decisions)` for a stage change with two decisions,
    `framing → code (+1 decision)` with one, `+1 decision` for one decision alone; `--log` text appended; no log line for a title
    change alone; `set --stage <current>` writes no arrow.
18. An exception injected during the write (patched `os.replace`) leaves the previous
    journal intact and no temporary file behind.

**Stops, next, resume, list**

19. `stop corrected` without `--note` and `stop seen --about "a (b)"` are refused;
    `stop seen --about "merge ok"` appends `Stop at <stage> (merge ok): seen` to
    `Decisions` and `stop at <stage>: seen` to `Log`.
20. `next`: `clear_first=yes` before `review` and `acceptance`, `no` before `delivery`;
    `no` everywhere when `Size: small`; `next=closed` at `follow-up`.
21. `resume`: nothing without a journal; leaves out routine stops; keeps a `corrected` one;
    never exceeds 30 lines; exits 0 outside a git repository.
22. `list`: header and rows; `no journal` when empty; `key` prints every field, empty ones
    included, and `main_worktree=yes` from the main worktree, `no` from a linked one.
22b. `key --branch abc-7-x --pattern 'ABC-\d+'` from the default branch prints `key=ABC-7`
    and creates no file; `--branch 142-x` works on a detached HEAD; an invalid
    `--pattern` exits 1.

**Commands and close**

23. A `Stage command` that fails or exceeds its timeout does not change the exit code; it
    does not run when the command was refused; it receives `JAM_KEY`, `JAM_STAGE`,
    `JAM_REPO`, `JAM_PR` (empty when none), `JAM_WORKTREE` and the first line of
    `Resume here` as `JAM_RESUME`; a `Resume here` containing `$(touch pwned)` reaches it
    as plain text and creates no file.
24. `close`: refused without a PR; refused when the state command prints `OPEN`, fails or
    times out, or when no `PR state command` is set; archives when it prints `MERGED`; `--force` archives without a PR; an
    existing archive refuses before anything is written.

**Stats**

Fixture transcripts are written under a temporary `CLAUDE_CONFIG_DIR`.

25. Transcripts are found from the journal's `Worktree`, through a symlinked path too; a
    session whose first `cwd` is elsewhere is ignored; a session that moves to another
    directory keeps its later entries; entries after the bound are ignored, the bound of
    an archive converted from local time to UTC.
26. Agent time: prompt → assistant → hook attachment stamped before the tool result →
    tool result → assistant is busy from the prompt to the last assistant; a gap ending
    in a prompt, an `AskUserQuestion` answer, a `user_temporary` permission result, a
    notification or an `isMeta` message from another session is not; a background
    subagent overlapping the main session is counted once (union).
27. Tokens: three lines with one `message.id` and growing `output_tokens` count the
    maximum; a forked session in a second file of the same directory counts its shared
    messages and entries once; groups `main` and `jam:reviewer ×N` per model; a subagent
    without `.meta.json` is `unknown`; a subagent with no counted entry is not a run.
28. Prompts: a typed prompt, a prompt with only an image, and a human `queued_command`
    count; `isMeta`, `isCompactSummary`, `promptSource: system`, a task notification,
    `/clear` (`<command-name>`), a `<bash-stdout>` line, an Escape marker
    (`[Request interrupted by user…]`) and a tool result do not; an
    `AskUserQuestion` result is an answer; a subagent's first entry is not a prompt; a
    session with an `entrypoint: sdk-cli` entry is left out.
29. A truncated JSON line and an entry without `timestamp` are skipped; no transcript, or
    `Worktree: (none)`, gives the `unavailable` form and exit 0; a session with entries
    but no `usage` gives `suspect`, an empty session next to a normal one does not; at
    `close`, a `suspect` or `no transcript` writes one line to `jam-lessons.md` and
    stderr, `no worktree` writes none; a directory whose only session is `sdk-cli` gives
    `no session in the worktree`, reported too; five figures unavailable for one reason
    give one reason in the line; `<synthetic>` messages are left out of Tokens.
30. Corrected stops; findings from `review:` parts, including one after an arrow, one
    with nested parentheses holding digits, and `review: 1 blocking (…), 6 other (…)`
    giving 1 and 6; `runs` and `logged` both shown; elapsed starts
    at the first counted entry when it precedes `created`; duration rounding and the
    `999 600` → `1.0M` token format; elapsed computed on minutes as displayed; the
    `Source` line lists the versions found, `2.1.9–2.1.10` in numeric order.
30b. Diff: `PR size command` printing `62 1 3` gives `+62 −1 · 3 files`; no PR, no
    command, a failing or slow command, or `62 1` gives `unavailable (…)` and the other
    figures stay; it receives `JAM_PR`; `1 file` in the singular; at `close`, a failing
    command is reported on stderr, not in `jam-lessons.md`, and the close archives.
    Context: two `compact_boundary` entries, one `auto`, give
    `2 compactions (1 automatic)`; a session starting with `/clear` counts one clear;
    `1 compaction` and `1 clear` in the singular; a forked copy of a boundary counts once.
31. `close` writes `## Stats` between `Lessons` and `Log`, and a second close after a
    failed move replaces it; a transcript reader that raises still archives, with journal
    figures only; `stats` on an archive with `## Stats` prints it unchanged, without one
    computes; `show` and `resume` read a journal with `## Stats`; an active journal is
    never rendered with an empty `## Stats`.

## Done when

- Every test above passes in CI, and `ruff check` is clean.
- On a real repository: `key`, `init`, `set`, `stop`, `next`, `resume` and `list` run on a
  ticket branch, and the session-start hook shows the resume block after a `/clear`.
- On a real ticket that was neither resumed nor compacted, computed without a bound: output tokens, main
  sessions and subagents together, within 5 % of the sum of each counted session's last
  `cost-state` record (which includes its subagents); agent time, main sessions and
  subagents together, within 10 % of the sum of `totalAPIDuration` and
  `totalToolDuration` in those same records, Claude Code's own measure of time spent in
  the model and in tools. Measured on three tickets: tokens −0.4 % to −1.0 %, time
  −0.5 % to −2.3 %. Time also held within 1 % on two compacted ones.
