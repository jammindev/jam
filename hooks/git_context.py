#!/usr/bin/env python3
"""UserPromptSubmit hook: inject a one-line git state so the assistant never
loses track of the current worktree / branch.

Kept to two git invocations to stay cheap on every prompt.
stdout is appended to the conversation context.

NOT covered: a repo opened through a symlink (/tmp is /private/tmp on macOS)
reads as a secondary worktree even when it is the main one: the cwd is
joined as given, the git dir comes back resolved.
"""
import json
import os
import re
import subprocess
import sys


def git(cwd, *args, timeout=3):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True, text=True, timeout=timeout,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cwd = data.get("cwd") or os.getcwd()

    # One call for the paths: toplevel, this worktree's gitdir, the shared gitdir.
    paths = git(
        cwd, "rev-parse", "--show-toplevel", "--absolute-git-dir",
        "--git-common-dir",
    ).splitlines()
    if len(paths) < 3:
        sys.exit(0)
    toplevel, gitdir, common = paths[0], paths[1], paths[2]

    # One call for branch + ahead/behind + dirty files.
    status = git(cwd, "status", "--porcelain", "--branch")
    if not status:
        sys.exit(0)
    head, *files = status.splitlines()

    branch = "(HEAD détachée)"
    match = re.match(r"## (?:No commits yet on )?([^.\s]+(?:\.[^.\s]+)*)", head)
    if match:
        branch = match.group(1)
    if "no branch" in head:
        branch = "(HEAD détachée)"

    parts = [f"worktree={os.path.basename(toplevel)}", f"branche={branch}"]

    tracking = re.search(r"\[(.*?)\]", head)
    if tracking:
        parts.append(tracking.group(1).replace("ahead ", "↑").replace("behind ", "↓"))
    elif "..." not in head:
        parts.append("pas d'upstream")

    dirty = len([f for f in files if f.strip()])
    if dirty:
        parts.append(f"{dirty} fichier(s) non commité(s)")

    if os.path.abspath(
        os.path.join(cwd, common)
    ) != os.path.abspath(gitdir):
        parts.append("(worktree secondaire)")

    # [jam] first, like every message of the plugin.
    print("[jam] [état git] " + " · ".join(parts))
    sys.exit(0)


if __name__ == "__main__":
    main()
