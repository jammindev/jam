#!/usr/bin/env python3
"""Tests for orca_cli.py — where the Orca binary is, and how it is called.

The lookup is tested with explicit environments and a replaced APP_BIN, so the
cases hold whether or not the Orca app is installed on the machine. Calls go to
the fake CLI of fixtures/fake_orca.py.

Run: python3 -m unittest scripts.test_orca_cli
"""

import os
import shutil
import tempfile
import unittest
from unittest import mock

from scripts import orca_cli
from scripts.fixtures.fake_orca import FakeOrca, failure, fixture, garbage, reply


class FindBinaryTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="orca-cli-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.on_path = FakeOrca(os.path.join(self.root, "on-path")).binary
        self.explicit = FakeOrca(os.path.join(self.root, "explicit")).binary
        self.app = FakeOrca(os.path.join(self.root, "app")).binary
        self.empty = os.path.join(self.root, "empty")
        os.makedirs(self.empty)
        self.missing = os.path.join(self.root, "nowhere", "orca")

    def find(self, env, app=None):
        with mock.patch.object(orca_cli, "APP_BIN", app or self.missing):
            return orca_cli.find_binary(env)

    def test_explicit_variable_first(self):
        env = {"JAM_ORCA_BIN": self.explicit, "PATH": os.path.dirname(self.on_path)}
        self.assertEqual(self.find(env, app=self.app), self.explicit)

    def test_explicit_variable_not_executable_is_not_replaced(self):
        # An explicit choice that fails is reported, never swapped silently.
        env = {"JAM_ORCA_BIN": self.missing, "PATH": os.path.dirname(self.on_path)}
        self.assertIsNone(self.find(env, app=self.app))

    def test_blank_variable_ignored(self):
        env = {"JAM_ORCA_BIN": "  ", "PATH": os.path.dirname(self.on_path)}
        self.assertEqual(self.find(env), self.on_path)

    def test_path_before_app(self):
        env = {"PATH": self.empty + os.pathsep + os.path.dirname(self.on_path)}
        self.assertEqual(self.find(env, app=self.app), self.on_path)

    def test_app_location_last(self):
        self.assertEqual(self.find({"PATH": self.empty}, app=self.app), self.app)

    def test_broken_symlink_on_path_skipped(self):
        links = os.path.join(self.root, "links")
        os.makedirs(links)
        os.symlink(self.missing, os.path.join(links, "orca"))
        self.assertEqual(self.find({"PATH": links}, app=self.app), self.app)

    def test_nothing_found(self):
        self.assertIsNone(self.find({"PATH": self.empty}))

    def test_not_found_message_has_no_path(self):
        self.assertIn("CLI Orca introuvable", orca_cli.NOT_FOUND)
        self.assertNotIn("/", orca_cli.NOT_FOUND)


class CallTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="orca-cli-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.fake = FakeOrca(os.path.join(self.root, "fake"))

    def call(self, *args, **kwargs):
        kwargs.setdefault("binary", self.fake.binary)
        return orca_cli.call(*args, **kwargs)

    def test_returns_result_and_adds_json_flag(self):
        self.fake.respond("worktree ps", reply(fixture("worktree-ps")))
        result = self.call("worktree", "ps")
        self.assertEqual(result["worktrees"][1]["displayName"], "22-tache")
        self.assertEqual(self.fake.calls(), [["worktree", "ps", "--json"]])

    def test_arguments_passed_untouched(self):
        self.fake.respond("terminal send", reply(fixture("terminal-send")))
        text = "brief  sur\ndeux lignes « avec » des espaces"
        self.call("terminal", "send", "--terminal", "term_1", "--text", text, "--enter")
        self.assertEqual(self.fake.calls(), [["terminal", "send", "--terminal", "term_1",
                                              "--text", text, "--enter", "--json"]])

    def test_failure_exit(self):
        self.fake.respond("worktree ps", failure(1, "orca: app not running"))
        with self.assertRaises(orca_cli.OrcaError) as caught:
            self.call("worktree", "ps")
        self.assertIn("orca worktree ps", str(caught.exception))
        self.assertIn("app not running", str(caught.exception))

    def test_unreadable_json(self):
        self.fake.respond("worktree ps", garbage())
        with self.assertRaises(orca_cli.OrcaError):
            self.call("worktree", "ps")

    def test_unexpected_shapes(self):
        for document in ({"ok": False, "result": {}}, {"ok": True, "result": []},
                         {"ok": True}, [1, 2], "result"):
            with self.subTest(document=document):
                self.fake.respond("worktree ps", reply(document))
                with self.assertRaises(orca_cli.OrcaError):
                    self.call("worktree", "ps")

    def test_timeout(self):
        self.fake.respond("terminal wait", reply(fixture("terminal-wait"), sleep=3))
        with self.assertRaises(orca_cli.OrcaError) as caught:
            self.call("terminal", "wait", timeout=0.5)
        self.assertIn("orca terminal wait", str(caught.exception))

    def test_binary_not_found(self):
        missing = os.path.join(self.root, "nowhere", "orca")
        with mock.patch.dict(os.environ, {"JAM_ORCA_BIN": missing}):
            with self.assertRaises(orca_cli.OrcaError) as caught:
                orca_cli.call("worktree", "ps")
        self.assertEqual(str(caught.exception), orca_cli.NOT_FOUND)


if __name__ == "__main__":
    unittest.main(verbosity=2)
