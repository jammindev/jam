#!/usr/bin/env python3
"""Tests for guard_outbound.py — the PreToolUse guard of commit, push and gh writes.

Each case runs the hook the way Claude Code does: a PreToolUse JSON payload on
stdin, the verdict read from the exit code (0 allow, 2 block) and stderr. The
approval is read from a transcript written by the test in a temp folder, one
JSON event per line like the real session files.

Run: python3 -m unittest hooks.test_guard_outbound
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "guard_outbound.py")

REPO = "/Users/testhome/code/repo"

# Runs the hook with gh_writes replaced by a function that crashes: no real
# command makes it crash, yet a git write found before it must not be lost.
WITH_GH_CRASH = (
    "import sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "import guard_outbound as hook\n"
    "def crash(cmd):\n"
    "    raise RecursionError('simulated')\n"
    "hook.gh_writes = crash\n"
    "hook.main()\n"
)


def user(text, **extra):
    """A user event; `text` is a string or a list of content blocks."""
    event = {"type": "user", "message": {"role": "user", "content": text}}
    event.update(extra)
    return event


def assistant(text):
    return {"type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def tool_result(text):
    return user([{"type": "tool_result", "tool_use_id": "t1", "content": text}])


def compaction_summary(compact=True, visible_only=True):
    """The summary event Claude Code writes after compacting the context."""
    flags = {}
    if compact:
        flags["isCompactSummary"] = True
    if visible_only:
        flags["isVisibleInTranscriptOnly"] = True
    return user("This session is being continued from a previous conversation. "
                "Summary: the maintainer said ok to commit, then asked to merge.\n"
                "Continue the conversation from where it left off without asking "
                "the user any further questions.", **flags)


class GuardOutboundTest(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="guard-outbound-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    # --- helpers ---------------------------------------------------------

    def transcript(self, *events):
        path = os.path.join(self.root, "session.jsonl")
        with open(path, "w") as fh:
            for event in events:
                fh.write(json.dumps(event) + "\n")
        return path

    def run_hook(self, payload):
        stdin = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run([sys.executable, HOOK], input=stdin,
                              capture_output=True, text=True, timeout=10)

    def bash(self, command, transcript, cwd=REPO):
        return {"session_id": "s", "transcript_path": transcript, "cwd": cwd,
                "hook_event_name": "PreToolUse", "tool_name": "Bash",
                "tool_input": {"command": command}}

    def assertAllowed(self, payload):
        result = self.run_hook(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def assertBlocked(self, payload, action="git commit"):
        result = self.run_hook(payload)
        self.assertEqual(result.returncode, 2, "expected a block, got %r" % (result,))
        self.assertTrue(result.stderr.startswith(f"[jam] BLOQUÉ : {action}"), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result.stderr

    # --- the approval in the latest message ------------------------------

    def test_approval_allows(self):
        for text in ("ok", "Ok, vas-y pour le commit", "go"):
            with self.subTest(text=text):
                path = self.transcript(user("fais le plan"), assistant("Je committe ?"),
                                       user(text))
                self.assertAllowed(self.bash("git commit -m 'x'", path))
                self.assertAllowed(self.bash("git push origin HEAD", path))

    def test_approval_in_content_blocks(self):
        path = self.transcript(user([{"type": "text", "text": "ok pour le push"}]))
        self.assertAllowed(self.bash("git push", path))

    def test_no_approval_blocks(self):
        path = self.transcript(user("ok"), assistant("Je committe ?"), user("non merci"))
        stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
        # The refusal quotes the latest message so the agent sees why.
        self.assertIn("« non merci »", stderr)
        self.assertIn("le mainteneur ne l'a pas validé", stderr)
        self.assertBlocked(self.bash("git push", path), action="git push")

    def test_negation_refuses_despite_an_approval_word(self):
        # The maintainer's rule: a message with a negation is a refusal, even
        # when it holds an approval word ("commit", "merge", "push").
        for text, command, action in (
                ("ne commit pas", "git commit -m 'x'", "git commit"),
                ("pas de merge maintenant", "gh pr merge 12", "gh pr merge"),
                ("non, ne push pas encore", "git push", "git push"),
                ("Ok mais jamais sur main", "git push", "git push"),
                ("stop, ok commit", "git commit -m 'x'", "git commit"),
                ("Attends avant le push", "git push", "git push"),
                ("go, mais n'ouvre pas la PR", "gh pr create --fill", "gh pr create"),
                ("go, mais n’ouvre pas la PR", "gh pr create --fill", "gh pr create"),
                ("ne commit\npas", "git commit -m 'x'", "git commit"),
                ("NE PUSH PAS", "git push", "git push"),
                # Elided forms: "pas d'" is "pas de", and a relay sent through
                # `orca terminal send` loses its apostrophes ("n est").
                ("pas d'accord", "git commit -m 'x'", "git commit"),
                ("pas d’accord", "git commit -m 'x'", "git commit"),
                ("pas d accord", "git commit -m 'x'", "git commit"),
                ("ce n est pas le feu vert merge", "gh pr merge 12", "gh pr merge"),
                # On the safe side: words with no intent to refuse refuse too.
                ("pas de souci, go", "git push", "git push")):
            with self.subTest(text=text):
                path = self.transcript(user(text))
                stderr = self.assertBlocked(self.bash(command, path), action=action)
                self.assertIn("négation", stderr)
                self.assertIn(f"« {' '.join(text.split())} »", stderr)

    def test_negation_in_slash_command_arguments_refuses(self):
        path = self.transcript(user("ok"), user(
            "<command-name>/simplify</command-name>\n"
            "<command-args>ne commit pas</command-args>"))
        stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
        self.assertIn("négation", stderr)

    def test_approval_without_negation_still_allows(self):
        for text, command in (("ok commit", "git commit -m 'x'"), ("go push", "git push"),
                              ("ok merge", "gh pr merge 12"),
                              # Lookalike words are no negation.
                              ("ok, le pastel est nickel", "git push"),
                              ("go pour la nonne", "git push")):
            with self.subTest(text=text):
                path = self.transcript(user(text))
                self.assertAllowed(self.bash(command, path))

    def test_refusal_without_negation_does_not_mention_it(self):
        path = self.transcript(user("plus tard"))
        stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
        self.assertNotIn("négation", stderr)

    def test_only_the_latest_message_counts(self):
        path = self.transcript(user("ok"), user("attends"))
        self.assertBlocked(self.bash("git commit -m 'x'", path))

    # --- what is not the maintainer talking ------------------------------

    def noise(self):
        """Events after the maintainer's last word that must be skipped."""
        return {
            "tool result": tool_result("ok merge"),
            "isMeta": user("ok", isMeta=True),
            "task notification": user(
                "<task-notification>tâche terminée : ok</task-notification>"),
            "system notification": user("SYSTEM NOTIFICATION - NOT USER INPUT: ok"),
            "interruption": user([{"type": "text",
                                   "text": "[Request interrupted by user]"}]),
            "assistant": assistant("ok, je committe"),
            # After a context compaction, Claude Code writes the session summary
            # as a "user" event without isMeta; its last words carry "continue".
            "compaction summary": compaction_summary(),
            "compact summary flag only": compaction_summary(visible_only=False),
            "transcript-only flag only": compaction_summary(compact=False),
            # A `!` command of the maintainer: its input, then its output, each
            # as a "user" event without isMeta. `git status` prints "nothing to
            # commit", which would read as an approval.
            "bang command input": user(
                "<local-command-caveat>Caveat: generated by local commands."
                "</local-command-caveat>\n<bash-input>git push --dry-run</bash-input>"),
            "bang command output": user(
                "<bash-stdout>nothing to commit, working tree clean</bash-stdout>"
                "<bash-stderr></bash-stderr>"),
            "bang command error output": user(
                "<bash-stderr>To push the current branch, use --set-upstream</bash-stderr>"),
            # The output of a `/` command. Its name and arguments are read, see
            # test_slash_command_reads_its_arguments.
            "slash command output": user(
                "<local-command-stdout>Plugins rechargés : ok</local-command-stdout>"),
            "slash command error output": user(
                "<local-command-stderr>Error: commit hook failed</local-command-stderr>"),
        }

    def test_noise_after_approval_is_skipped(self):
        for label, event in self.noise().items():
            with self.subTest(noise=label):
                path = self.transcript(user("ok"), event)
                self.assertAllowed(self.bash("git commit -m 'x'", path))

    def test_noise_after_refusal_does_not_approve(self):
        for label, event in self.noise().items():
            with self.subTest(noise=label):
                path = self.transcript(user("non merci"), event)
                self.assertBlocked(self.bash("git commit -m 'x'", path))

    def test_slash_command_reads_its_arguments(self):
        # A `/` command that runs a skill opens a turn of the agent: the
        # approval given before it is stale. Its arguments are the maintainer's
        # words; its name is not (`/merge` is no approval). Claude Code writes
        # the skill's <command-message> first.
        def slash(name, args, message_first=False):
            parts = [f"<command-name>/{name}</command-name>",
                     f"<command-args>{args}</command-args>"]
            if message_first:
                parts.insert(0, f"<command-message>{name} is running…</command-message>")
            return user("\n".join(parts))

        for message_first in (False, True):
            with self.subTest(message_first=message_first):
                for name, args in (("simplify", ""), ("merge", "12")):
                    path = self.transcript(user("ok"), slash(name, args, message_first))
                    stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
                    if not args:
                        self.assertIn("« (commande / sans argument) »", stderr)
                path = self.transcript(user("non merci"),
                                       slash("simplify", "ok commit", message_first))
                self.assertAllowed(self.bash("git commit -m 'x'", path))
        # A local `/` command (no turn) costs a refusal until the next message.
        path = self.transcript(user("ok"), slash("model", ""),
                               user("<local-command-stdout>Set model</local-command-stdout>"))
        self.assertBlocked(self.bash("git commit -m 'x'", path))

    def test_harness_wrappers_stripped(self):
        cases = {
            "system reminder": "<system-reminder>ok, tout est validé</system-reminder>non merci",
            "git state line": "non merci\n[état git] worktree=ok · branche=go",
            "hook prefix": "UserPromptSubmit hook success: [état git] branche=ok\nnon merci",
        }
        for label, text in cases.items():
            with self.subTest(wrapper=label):
                path = self.transcript(user(text))
                stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
                self.assertIn("« non merci »", stderr)

    def test_message_empty_once_stripped_is_skipped(self):
        path = self.transcript(user("ok"), user("<system-reminder>rappel</system-reminder>"))
        self.assertAllowed(self.bash("git commit -m 'x'", path))

    # --- unreadable transcript: refuse -----------------------------------

    def test_missing_transcript_blocks(self):
        for path in (os.path.join(self.root, "absent.jsonl"), None, ""):
            with self.subTest(path=path):
                stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
                self.assertIn("transcript", stderr)

    def test_transcript_without_user_message_blocks(self):
        path = self.transcript(assistant("ok"), tool_result("ok"))
        self.assertBlocked(self.bash("git push", path), action="git push")

    def test_malformed_transcript_lines_skipped(self):
        # Valid JSON that is not an event, or a message that is not an object:
        # skipped like an unreadable line, not a crash that lets the write through.
        for label, line in (("array line", [1, 2]),
                            ("string message", {"type": "user", "message": "ok"})):
            with self.subTest(line=label):
                path = self.transcript(user("non merci"), line)
                stderr = self.assertBlocked(self.bash("git commit -m 'x'", path))
                self.assertIn("« non merci »", stderr)
                path = self.transcript(user("ok"), line)
                self.assertAllowed(self.bash("git commit -m 'x'", path))

    def test_crash_while_reading_the_approval_blocks(self):
        # A text block set to null makes the reading fail: an approval that
        # cannot be checked is no approval.
        path = self.transcript(user("ok"), user([{"type": "text", "text": None}]))
        for command, action in (("git commit -m 'x'", "git commit"),
                                ("gh pr merge 1", "gh pr merge")):
            with self.subTest(command=command):
                stderr = self.assertBlocked(self.bash(command, path), action=action)
                self.assertIn("plant", stderr)
        # No write recognised: the transcript is not even read.
        self.assertAllowed(self.bash("git status", path))

    def test_crash_in_gh_reading_keeps_the_git_write(self):
        path = self.transcript(user("ok"))

        def run(command):
            return subprocess.run([sys.executable, "-c", WITH_GH_CRASH, HERE],
                                  input=json.dumps(self.bash(command, path)),
                                  capture_output=True, text=True, timeout=10)

        result = run("git commit -m 'x'")
        self.assertEqual(result.returncode, 2, result)
        self.assertTrue(result.stderr.startswith("[jam] BLOQUÉ : git commit"), result.stderr)
        self.assertIn("plant", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        # No git write found before the crash: nothing recognised, let through.
        result = run("git status")
        self.assertEqual((result.returncode, result.stderr), (0, ""))

    # --- which commands are covered --------------------------------------

    def test_command_forms_blocked(self):
        path = self.transcript(user("non merci"))
        for command, action in (("git -C x commit -m 'x'", "git commit"),
                                ("git -C /some/repo push", "git push"),
                                ("rtk git push origin main", "git push"),
                                ("cd sub && git commit -am 'x'", "git commit"),
                                ("GIT_EDITOR=true git commit --amend", "git commit"),
                                ("git \\\n  commit -m x", "git commit"),
                                # Global options between git and the verb.
                                ("git -c commit.gpgsign=false commit -m x", "git commit"),
                                ("git -c 'user.name=A B' push", "git push"),
                                ('git -c user.name="A B" commit -m x', "git commit"),
                                ('git -C ~/"a b" commit -m x', "git commit"),
                                ("git -C /a\\ b push", "git push"),
                                ('git -C "/chemin avec espace" commit -m x', "git commit"),
                                ("git -C '/chemin avec espace' push", "git push"),
                                ("git --no-pager push", "git push"),
                                ("git -P commit -m x", "git commit"),
                                ("git --git-dir=/r/.git --work-tree=/r commit -m x",
                                 "git commit"),
                                ("git --git-dir /r/.git push", "git push"),
                                ("git -C x -c core.pager=cat --no-pager commit -m x",
                                 "git commit")):
            with self.subTest(command=command):
                self.assertBlocked(self.bash(command, path), action=action)

    def test_dry_run_allowed(self):
        path = self.transcript(user("non merci"))
        self.assertAllowed(self.bash("git push --dry-run origin HEAD", path))
        self.assertAllowed(self.bash("git commit --dry-run -m 'x'", path))
        self.assertAllowed(self.bash("git --no-pager push --dry-run", path))

    def test_other_commands_allowed(self):
        path = self.transcript(user("non merci"))
        for command in ("git status", "git diff --stat", "git log --oneline -5",
                        "gh pr view 12", "ls commit/", "git --no-pager log --grep commit",
                        "git -C x status", "git -c core.pager=cat diff",
                        "git -c alias.ci=commit status"):
            with self.subTest(command=command):
                self.assertAllowed(self.bash(command, path))

    def test_session_scratch_dirs_allowed(self):
        path = self.transcript(user("non merci"))
        for cwd in ("/tmp/claude-x/repo", "/private/tmp/claude-501/s/scratchpad"):
            with self.subTest(cwd=cwd):
                self.assertAllowed(self.bash("git commit -m 'x'", path, cwd=cwd))
                self.assertAllowed(self.bash("git push", path, cwd=cwd))
        # Only the cwd counts, not a lookalike folder.
        self.assertBlocked(self.bash("git commit -m 'x'", path, cwd="/tmp/claudette"))

    def test_other_tools_allowed(self):
        path = self.transcript(user("non merci"))
        payload = self.bash("git commit -m 'x'", path)
        payload["tool_name"] = "Edit"
        self.assertAllowed(payload)

    def test_invalid_input_allowed(self):
        # Not the payload Claude Code sends: nothing to read a write from.
        for raw in ("{not json", "", "[]",
                    json.dumps({"tool_name": "Bash", "tool_input": "git commit -m x"})):
            with self.subTest(raw=raw):
                self.assertAllowed(raw)

    # --- gh: one outbound guard for every remote write (annex B) ---------

    GH_WRITES = (
        ["gh pr " + s + " 12" for s in ("create", "merge", "close", "reopen", "edit",
                                        "comment", "review", "ready")]
        + ["gh issue " + s + " 12" for s in ("create", "close", "reopen", "edit", "comment",
                                             "delete", "transfer", "lock", "unlock", "pin",
                                             "unpin", "develop")]
        + ["gh release " + s + " v1" for s in ("create", "edit", "delete", "upload")]
        + ["gh repo " + s + " o/r" for s in ("create", "edit", "delete", "rename", "archive",
                                             "fork", "sync")]
        + ["gh label " + s + " bug" for s in ("create", "edit", "delete")]
        + ["gh workflow " + s + " ci.yml" for s in ("run", "enable", "disable")]
        + ["gh run " + s + " 42" for s in ("rerun", "cancel", "delete")]
        + ["gh secret set TOKEN", "gh variable set NAME", "gh variable delete NAME",
           "gh gist create notes.md", "gh gist edit 1", "gh gist delete 1",
           "gh api -X POST repos/o/r/issues", "gh api --method=DELETE repos/o/r/labels/x",
           "gh api -XPATCH repos/o/r/pulls/1",
           "gh api repos/o/r/milestones -f title=v1",
           "gh api repos/o/r/pulls/1/merge -X PUT",
           "gh api repos/o/r/issues --input body.json",
           "gh api repos/o/r/issues -F title=@t.txt",
           "gh api repos/o/r/issues --raw-field title=x",
           "gh api repos/o/r/issues --field=title=x",
           "gh api graphql -f query='mutation { addStar(input: {}) { clientMutationId } }'",
           # A GraphQL query the guard cannot read (file or stdin) counts as a write.
           "gh api graphql --input q.json", "gh api graphql --input=q.json",
           "gh api graphql --input - <<'EOF'\nmutation { addStar(input: {}) { x } }\nEOF",
           "gh api graphql -F query=@q.graphql",
           "gh api graphql --field query=@q.graphql",
           "gh api graphql --field=query=@q.graphql",
           "gh api graphql -Fquery=@q.graphql",
           # Forms the guard must see through.
           "rtk gh pr create --fill", "rtk proxy gh pr merge 1",
           "gh -R o/r issue create --title t",
           "gh --repo o/r pr merge 1", "gh --repo=o/r pr merge 1",
           "gh issue create -R o/r --title t", "/usr/local/bin/gh pr merge 1",
           "GH_TOKEN=x gh pr merge 1", "gh pr view 1 && gh pr merge 1",
           "git status; gh issue comment 3 --body ok", "bash -c 'gh pr merge 1'",
           # Command substitutions, quoted or in backticks.
           'PR="$(gh pr create --fill)"', 'echo "$(gh pr merge 1)"',
           "echo `gh pr merge 1`", "X=`gh pr merge 1`",
           # Line continuations: the multiline form of the GitHub REST docs.
           "gh api \\\n  --method POST \\\n  repos/o/r/issues \\\n  -f title=x",
           "gh \\\n  pr merge 1",
           "gh api -X PATCH repos/o/r/issues/1", "gh api repos/o/r/labels -f x=y",
           # A gh command that is neither on the read list nor parseable.
           "gh issue create --title 'l", "gh alias set co 'pr checkout'"]
    )

    GH_READS = (
        "gh pr list", "gh pr view 12 --json title,body", "gh pr status", "gh pr diff 3",
        "gh pr checks 3", "gh pr checkout 3", "gh issue list --limit 20", "gh issue view 7",
        "gh issue status", "gh repo view o/r", "gh repo list o", "gh repo clone o/r",
        "gh run list", "gh run view 42 --log", "gh run watch 42", "gh run download 42",
        "gh workflow list", "gh workflow view ci.yml", "gh release list",
        "gh release view v1", "gh release download v1", "gh label list",
        "gh search issues 'is:open label:bug'", "gh status", "gh browse", "gh auth status",
        "gh help", "gh version", "gh --version",
        "gh api repos/o/r/pulls", "gh api -X GET repos/o/r", "gh api --method HEAD repos/o/r",
        "gh api repos/o/r/issues --jq '.[].title' -H 'Accept: application/json'",
        "gh api graphql -f query='query { viewer { login } }'",
        "gh api graphql -F owner=o -f query='query($owner: String!) { user(login: $owner) { id } }'",
        "rtk gh pr list", "rtk proxy gh pr list", "gh -R o/r pr view 3",
        "/usr/local/bin/gh issue list",
        # Help only: bare gh, gh --help, a command without its subcommand.
        "gh", "gh --help", "gh pr",
        "gh pr view 1 | head", "cat gh.txt", "which gh", "ls ~/gh/",
        'echo "$(gh pr view 1)"',
        "gh api \\\n  repos/o/r/pulls \\\n  --jq '.[].title'",
    )

    def test_gh_writes_blocked_without_approval(self):
        path = self.transcript(user("non merci"))
        for command in self.GH_WRITES:
            with self.subTest(command=command):
                stderr = self.assertBlocked(self.bash(command, path), action="gh")
                self.assertIn("« non merci »", stderr)

    def test_gh_writes_allowed_after_approval(self):
        path = self.transcript(user("ok"))
        for command in self.GH_WRITES:
            with self.subTest(command=command):
                self.assertAllowed(self.bash(command, path))

    def test_gh_label_names_the_action(self):
        path = self.transcript(user("non merci"))
        self.assertBlocked(self.bash("gh -R o/r pr merge 12 --squash", path),
                           action="gh pr merge")
        self.assertBlocked(self.bash("gh api -X PATCH repos/o/r", path), action="gh api")

    def test_gh_reads_never_blocked(self):
        # Not even when the transcript cannot be read: a read needs no approval.
        refused = self.transcript(user("non merci"))
        for path in (refused, None):
            for command in self.GH_READS:
                with self.subTest(command=command, transcript=path):
                    self.assertAllowed(self.bash(command, path))

    def test_scratch_exemption_not_for_gh(self):
        # gh writes remotely wherever it runs from.
        path = self.transcript(user("non merci"))
        self.assertBlocked(self.bash("gh pr create --fill", path, cwd="/tmp/claude-x/repo"),
                           action="gh pr create")

    def test_green_light_relayed_by_a_card_is_not_an_approval(self):
        # The maintainer's last word is no approval; the green light only shows
        # in a tool result (a card read by the agent): refused. Then the
        # maintainer gives it in their own message: allowed.
        card = ("22-tache · in-review · ⏸ attente merge · "
                "✓ feu vert merge : « ok merge » (20:09, session du coordinateur)")
        path = self.transcript(user("surveille les cartes"),
                               assistant("Je lis les cartes."), tool_result(card))
        self.assertBlocked(self.bash("gh pr merge 12", path), action="gh pr merge")
        # Same after a compaction: hours of watching the cards compact the
        # context, and the summary is no word from the maintainer.
        path = self.transcript(user("surveille les cartes"), tool_result(card),
                               compaction_summary(), assistant("Je relis les cartes."),
                               tool_result(card))
        self.assertBlocked(self.bash("gh pr merge 12", path), action="gh pr merge")
        path = self.transcript(user("surveille les cartes"), tool_result(card),
                               user("ok merge"))
        self.assertAllowed(self.bash("gh pr merge 12", path))

    def test_marked_git_state_line_stripped(self):
        for text in ("non merci\n[jam] [état git] worktree=ok · branche=go",
                     "UserPromptSubmit hook success: [jam] [état git] branche=ok\nnon merci"):
            with self.subTest(text=text):
                path = self.transcript(user(text))
                stderr = self.assertBlocked(self.bash("gh pr merge 1", path), action="gh")
                self.assertIn("« non merci »", stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
