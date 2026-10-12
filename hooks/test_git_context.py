#!/usr/bin/env python3
"""Tests for git_context.py — the one-line git state added to every prompt.

Each case runs the hook the way Claude Code does: a UserPromptSubmit JSON
payload on stdin, the line read on stdout. The repos are real ones, made by the
test in a temp folder with an isolated HOME, so no personal git config leaks in.

Run: python3 -m unittest hooks.test_git_context
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "git_context.py")


class GitContextTest(unittest.TestCase):

    def setUp(self):
        # realpath: git reports resolved paths (/private/var on macOS), and the
        # hook compares them with the cwd it receives.
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="git-context-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    # --- fixtures --------------------------------------------------------

    def env(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update({"HOME": self.root, "GIT_CEILING_DIRECTORIES": self.root,
                    "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
                    "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com"})
        return env

    def git(self, cwd, *args):
        subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                       env=self.env(), check=True)

    def make_repo(self, name="repo", commit=False):
        path = os.path.join(self.root, name)
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", path],
                       capture_output=True, env=self.env(), check=True)
        if commit:
            self.git(path, "commit", "-q", "--allow-empty", "-m", "init")
        return path

    def run_hook(self, cwd, stdin=None):
        done = subprocess.run(
            [sys.executable, HOOK],
            input=json.dumps({"cwd": cwd}) if stdin is None else stdin,
            capture_output=True, text=True, env=self.env(), timeout=30,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stderr, "")
        return done.stdout

    # --- cases -----------------------------------------------------------

    def test_outside_a_repo_is_silent(self):
        outside = os.path.join(self.root, "not-a-repo")
        os.makedirs(outside)
        self.assertEqual(self.run_hook(outside), "")

    def test_invalid_input_is_silent(self):
        self.assertEqual(self.run_hook(None, stdin="{not json"), "")

    def test_new_repo(self):
        repo = self.make_repo()
        self.assertEqual(self.run_hook(repo),
                         "[jam] [état git] worktree=repo · branche=main · pas d'upstream\n")

    def test_dirty_files_counted(self):
        repo = self.make_repo(commit=True)
        for name in ("a.txt", "b.txt"):
            with open(os.path.join(repo, name), "w") as fh:
                fh.write("x\n")
        out = self.run_hook(repo)
        self.assertEqual(out, "[jam] [état git] worktree=repo · branche=main · pas d'upstream"
                              " · 2 fichier(s) non commité(s)\n")

    def test_ahead_of_upstream(self):
        origin = self.make_repo("origin", commit=True)
        clone = os.path.join(self.root, "clone")
        subprocess.run(["git", "clone", "-q", origin, clone], capture_output=True,
                       env=self.env(), check=True)
        self.git(clone, "commit", "-q", "--allow-empty", "-m", "local")
        out = self.run_hook(clone)
        self.assertEqual(out, "[jam] [état git] worktree=clone · branche=main · ↑1\n")
        self.assertNotIn("pas d'upstream", out)

    def test_secondary_worktree_flagged(self):
        repo = self.make_repo(commit=True)
        other = os.path.join(self.root, "other-wt")
        self.git(repo, "worktree", "add", "-q", "-b", "feature", other)
        out = self.run_hook(other)
        self.assertTrue(out.startswith("[jam] [état git] "), out)
        self.assertIn("worktree=other-wt · branche=feature", out)
        self.assertTrue(out.rstrip("\n").endswith(" · (worktree secondaire)"), out)
        self.assertNotIn("worktree secondaire", self.run_hook(repo))

    def test_detached_head(self):
        repo = self.make_repo(commit=True)
        self.git(repo, "checkout", "-q", "--detach")
        out = self.run_hook(repo)
        self.assertTrue(out.startswith("[jam] [état git] "), out)
        self.assertIn("branche=(HEAD détachée)", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
