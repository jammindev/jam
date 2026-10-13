#!/usr/bin/env python3
"""Tests for the plugin wiring: .claude-plugin/ and hooks/hooks.json.

Claude Code loads the plugin from these three files; a typo there silently
drops a guard. The tests read them as Claude Code does (plain JSON) and check
that every hook command points at a file that exists.

Run: python3 -m unittest hooks.test_plugin
"""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

EXPECTED_HOOKS = {
    # event: [(matcher, hook file), ...] in order
    "PreToolUse": [("Bash", "guard_outbound.py"),
                   ("Edit|Write|NotebookEdit|Bash", "guard_coordinator.py")],
    "UserPromptSubmit": [(None, "git_context.py")],
    "SessionStart": [("startup|clear", "session_start_recap.py")],
}
COMMAND = re.compile(r'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/([\w.]+)"')


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


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

    def test_hook_files_exist(self):
        for group_list in self.hooks["hooks"].values():
            for group in group_list:
                for hook in group["hooks"]:
                    name = COMMAND.fullmatch(hook["command"]).group(1)
                    with self.subTest(hook=name):
                        self.assertTrue(os.path.isfile(os.path.join(HERE, name)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
