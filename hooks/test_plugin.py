#!/usr/bin/env python3
"""Tests for the plugin wiring (.claude-plugin/, hooks/hooks.json) and its method.

Claude Code loads the plugin from these three files; a typo there silently
drops a guard. The tests read them as Claude Code does (plain JSON) and check
that every hook command points at a file that exists. They also hold the
method in process/ and roles/ to its word cap (NFR-015) and keep it generic
(NFR-014).

Run: python3 -m unittest hooks.test_plugin
"""

import json
import os
import re
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

EXPECTED_HOOKS = {
    # event: [(matcher, hook file), ...] in order
    "PreToolUse": [("Bash", "guard_outbound.py"),
                   ("Edit|Write|NotebookEdit|Bash", "guard_coordinator.py")],
    "UserPromptSubmit": [(None, "git_context.py")],
    "SessionStart": [("startup|clear|resume", "session_start_recap.py")],
}
COMMAND = re.compile(r'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/([\w.]+)"')

# NFR-015: the method may hold at most half the words docs/process/ had on main
# when the pruning task started (9808 words at a4794df, counted like `wc -w`).
METHOD_WORD_CAP = 4904
METHOD_FILES = ["process/README.md", "process/fiche-projet.md"] + [
    f"roles/{role}.md" for role in ("coordinateur", "orchestrateur-tache", "redacteur",
                                     "planificateur", "implementeur", "relecteur",
                                     "recetteur")]
# NFR-014: nothing proper to one project or one machine. Other projects' names
# are checked at acceptance against a list that is never versioned.
FORBIDDEN_IN_METHOD = ["pnpm", "/Users/", "/home/"]


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


def method_pages(root):
    """The Markdown pages under process/ and roles/, as paths relative to root."""
    return sorted(f"{folder}/{name}" for folder in ("process", "roles")
                  for name in os.listdir(os.path.join(root, folder))
                  if name.endswith(".md"))


class PluginManifestTest(unittest.TestCase):

    def test_plugin_json(self):
        plugin = load(".claude-plugin", "plugin.json")
        self.assertEqual(plugin["name"], "jam")
        self.assertTrue(plugin["description"].strip())
        self.assertEqual(plugin["license"], "MIT")
        self.assertTrue(plugin["repository"].startswith("https://"))
        # Loaded in place from the clone: no version to bump, no author named.
        self.assertNotIn("version", plugin)
        self.assertNotIn("author", plugin)

    def test_marketplace_json(self):
        market = load(".claude-plugin", "marketplace.json")
        self.assertEqual(market["name"], "jam")
        self.assertTrue(market["owner"]["name"].strip())
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], "jam")
        # The plugin is the marketplace's own root.
        self.assertEqual(entry["source"], ".")


class HooksJsonTest(unittest.TestCase):

    def setUp(self):
        self.hooks = load("hooks", "hooks.json")

    def test_wrapped_in_hooks_key(self):
        # A file holding only the event map fails to load.
        self.assertIsInstance(self.hooks.get("hooks"), dict)
        self.assertLessEqual(set(self.hooks), {"description", "hooks"})

    def test_events_matchers_and_files(self):
        events = self.hooks["hooks"]
        self.assertEqual(set(events), set(EXPECTED_HOOKS))
        for event, expected in EXPECTED_HOOKS.items():
            with self.subTest(event=event):
                found = []
                for group in events[event]:
                    for hook in group["hooks"]:
                        self.assertEqual(hook["type"], "command")
                        match = COMMAND.fullmatch(hook["command"])
                        self.assertIsNotNone(match, hook["command"])
                        found.append((group.get("matcher"), match.group(1)))
                self.assertEqual(found, expected)

    def test_recap_on_start_clear_and_resume(self):
        # The coordinator resumes with --continue (source "resume"): without
        # the recap, a missing JAM_ROLE would go unwarned. A compaction keeps
        # the session's context, so it needs none.
        groups = self.hooks["hooks"]["SessionStart"]
        sources = {source for group in groups for source in group["matcher"].split("|")}
        self.assertLessEqual({"startup", "clear", "resume"}, sources)
        self.assertNotIn("compact", sources)

    def test_hook_files_exist(self):
        for group_list in self.hooks["hooks"].values():
            for group in group_list:
                for hook in group["hooks"]:
                    name = COMMAND.fullmatch(hook["command"]).group(1)
                    with self.subTest(hook=name):
                        self.assertTrue(os.path.isfile(os.path.join(HERE, name)))


class MethodTest(unittest.TestCase):
    """The method the plugin carries: process/ and roles/, generic and short."""

    def read(self, relative):
        with open(os.path.join(ROOT, relative), encoding="utf-8") as fh:
            return fh.read()

    def test_every_file_present(self):
        for relative in METHOD_FILES:
            with self.subTest(file=relative):
                self.assertTrue(os.path.isfile(os.path.join(ROOT, relative)))

    def test_no_file_left_uncounted(self):
        # A new file in process/ or roles/ must enter the count, not dodge it.
        self.assertEqual(method_pages(ROOT), sorted(METHOD_FILES))

    def test_only_pages_counted(self):
        # Finder (.DS_Store) and editors (README.md~) drop files there on the
        # maintainer's machine: they are not method pages and must not turn
        # the suite red.
        with tempfile.TemporaryDirectory() as root:
            for folder in ("process", "roles"):
                os.mkdir(os.path.join(root, folder))
            for relative in ("process/README.md", "process/README.md~",
                             "roles/.DS_Store", "roles/nouveau.md"):
                open(os.path.join(root, relative), "w").close()
            self.assertEqual(method_pages(root), ["process/README.md", "roles/nouveau.md"])

    def test_under_word_cap(self):
        counts = {relative: len(self.read(relative).split()) for relative in METHOD_FILES}
        words = sum(counts.values())
        self.assertLessEqual(words, METHOD_WORD_CAP, f"{words} mots : {counts}")

    def test_generic(self):
        for relative in METHOD_FILES:
            text = self.read(relative)
            for forbidden in FORBIDDEN_IN_METHOD:
                with self.subTest(file=relative, forbidden=forbidden):
                    # assertNotIn would print the whole file on failure.
                    self.assertFalse(forbidden in text, f"« {forbidden} » dans {relative}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
