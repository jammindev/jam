#!/usr/bin/env python3
"""Tests for guard_coordinator.py — the PreToolUse guard of the coordinator role.

Each case runs the hook the way Claude Code does: a PreToolUse JSON payload on
stdin, the verdict read from the exit code (0 allow, 2 block) and stderr. HOME is
a fake path so the memory and ~/.claude/hooks rules never depend on the real
machine; nothing is written, the guard only reasons on paths.

Run: python3 test_guard_coordinator.py
"""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "guard_coordinator.py")

HOME = "/Users/testhome"
REPO = HOME + "/code/repo"
MEMORY = HOME + "/.claude/projects/-Users-testhome-code-repo/memory"
SCRATCH = "/private/tmp/claude-501/session/scratchpad"
STAGING = SCRATCH + "/hooks-staging"
# The refusal points at the process of the plugin running the guard, found from
# the hook's own file: the session's repo may hold no process, or a stale copy.
PLUGIN_PROCESS = os.path.join(os.path.dirname(HERE), "process", "README.md")
REFUSAL = f"Le coordinateur ne produit pas de livrable : délègue à un rôle ({PLUGIN_PROCESS})."


class GuardCoordinatorTest(unittest.TestCase):

    # --- helpers ---------------------------------------------------------

    def run_hook(self, payload, role="coordinateur"):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": HOME}
        if role is not None:
            env["JAM_ROLE"] = role
        stdin = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run([sys.executable, HOOK], input=stdin, env=env,
                              capture_output=True, text=True, timeout=10)

    def tool(self, name, cwd=REPO, **tool_input):
        return {"session_id": "s", "transcript_path": "/nonexistent", "cwd": cwd,
                "hook_event_name": "PreToolUse", "tool_name": name,
                "tool_input": tool_input}

    def bash(self, command, cwd=REPO):
        return self.tool("Bash", cwd=cwd, command=command)

    def assertAllowed(self, payload, role="coordinateur"):
        result = self.run_hook(payload, role)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def assertBlocked(self, payload):
        result = self.run_hook(payload)
        self.assertEqual(result.returncode, 2, "expected a block, got %r" % (result,))
        self.assertTrue(result.stderr.startswith("[jam] BLOQUÉ : "), result.stderr)
        self.assertIn(REFUSAL, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    # --- role gate -------------------------------------------------------

    def test_other_roles_pass_silently(self):
        for role in (None, "", "implementeur", "relecteur"):
            with self.subTest(role=role):
                self.assertAllowed(self.tool("Edit", file_path=REPO + "/src/app.py"), role)
                self.assertAllowed(self.bash("sed -i '' 's/a/b/' src/app.py"), role)

    def test_role_is_normalised(self):
        result = self.run_hook(self.tool("Write", file_path=REPO + "/a.md"), role=" Coordinateur ")
        self.assertEqual(result.returncode, 2)

    # --- Edit / Write / NotebookEdit -------------------------------------

    def test_edit_repo_file_blocked(self):
        self.assertBlocked(self.tool("Edit", file_path=REPO + "/src/app.py",
                                     old_string="a", new_string="b"))

    def test_write_and_notebook_in_repo_blocked(self):
        self.assertBlocked(self.tool("Write", file_path=REPO + "/docs/plan.md", content="x"))
        self.assertBlocked(self.tool("NotebookEdit", notebook_path=REPO + "/nb.ipynb",
                                     new_source="x"))

    def test_relative_path_resolved_against_cwd(self):
        self.assertBlocked(self.tool("Write", file_path="docs/plan.md", content="x"))
        self.assertAllowed(self.tool("Write", cwd=SCRATCH, file_path="notes.md", content="x"))

    def test_edit_memory_allowed(self):
        self.assertAllowed(self.tool("Edit", file_path=MEMORY + "/MEMORY.md",
                                     old_string="a", new_string="b"))
        self.assertAllowed(self.tool("Write", file_path=MEMORY + "/sub/fact.md", content="x"))
        self.assertAllowed(self.tool("NotebookEdit", notebook_path=MEMORY + "/nb.ipynb",
                                     new_source="x"))

    def test_plan_mode_file_allowed(self):
        self.assertAllowed(self.tool("Write", file_path=HOME + "/.claude/plans/clever-canyon.md",
                                     content="x"))
        self.assertBlocked(self.tool("Write", file_path=HOME + "/.claude/plans/sub/x.md",
                                     content="x"))
        self.assertBlocked(self.tool("Write", file_path=HOME + "/.claude/plans/x.py",
                                     content="x"))

    def test_write_scratch_allowed(self):
        self.assertAllowed(self.tool("Write", file_path="/private/tmp/claude-x/brief.md",
                                     content="x"))
        self.assertAllowed(self.tool("Write", file_path="/tmp/claude-501/a/b.md", content="x"))

    def test_lookalike_paths_blocked(self):
        for path in ("/tmp/claude.md", "/tmp/other/claude-x/f.md",
                     HOME + "/.claude/projects/p/MEMORY.md",
                     HOME + "/.claude/projects/p/memory-old/f.md",
                     HOME + "/.claude/hooks/guard_coordinator.py",
                     HOME + "/.claude/settings.json"):
            with self.subTest(path=path):
                self.assertBlocked(self.tool("Write", file_path=path, content="x"))

    def test_dotdot_escape_blocked(self):
        self.assertBlocked(self.tool(
            "Write", file_path="/private/tmp/claude-x/../../../Users/testhome/code/repo/a.py",
            content="x"))
        self.assertBlocked(self.tool(
            "Edit", file_path=MEMORY + "/../../../settings.json",
            old_string="a", new_string="b"))
        # A .. that stays inside an allowed tree is fine.
        self.assertAllowed(self.tool("Write", file_path=MEMORY + "/sub/../fact.md",
                                     content="x"))

    # --- Bash: sed -i, redirections, tee, cp, mv --------------------------

    def test_sed_in_place_on_repo_blocked(self):
        self.assertBlocked(self.bash("sed -i '' 's/foo/bar/' src/app.py"))
        self.assertBlocked(self.bash("sed -i.bak -e 's/foo/bar/' " + REPO + "/src/app.py"))
        self.assertBlocked(self.bash("sed --in-place 's/a/b/' README.md"))

    def test_sed_read_or_scratch_allowed(self):
        self.assertAllowed(self.bash("sed -n '1,40p' src/app.py"))
        self.assertAllowed(self.bash("sed -i '' 's/a/b/' " + SCRATCH + "/notes.md"))

    def test_redirect_to_repo_blocked(self):
        self.assertBlocked(self.bash("cat notes.md > src/app.py"))
        self.assertBlocked(self.bash("echo x >> " + REPO + "/CHANGELOG.md"))
        self.assertBlocked(self.bash("ls\ncat a >src/out.txt"))
        self.assertBlocked(self.bash("make 2> build.log"))
        self.assertBlocked(self.bash("echo x &> out.log"))
        self.assertBlocked(self.bash("echo x >| out.log"))
        self.assertBlocked(self.bash("make &>> build.log"))

    def test_harmless_redirects_allowed(self):
        self.assertAllowed(self.bash("ls 2>&1"))
        self.assertAllowed(self.bash("pytest -q >/dev/null 2>&1"))
        self.assertAllowed(self.bash("echo oops >&2"))
        self.assertAllowed(self.bash("grep -r foo . 2>/dev/null | head"))
        self.assertAllowed(self.bash("git log --oneline > " + SCRATCH + "/log.txt"))

    def test_quoted_gt_allowed(self):
        self.assertAllowed(self.bash('echo "a > b"'))
        self.assertAllowed(self.bash("grep '>' src/app.py"))
        self.assertAllowed(self.bash('git commit -m "fix: \\"x\\" -> y > z"'))
        self.assertAllowed(self.bash("ls # cat a > src/app.py"))
        self.assertAllowed(self.bash(
            'orca terminal send --terminal t1 --text "écris le rapport > relecture.md"'))

    def test_unresolvable_redirect_target_blocked(self):
        self.assertBlocked(self.bash('echo x > "$OUT"'))
        self.assertBlocked(self.bash("echo x > $(mktemp)"))

    def test_home_variable_expanded(self):
        self.assertAllowed(self.bash('echo x > "$HOME/.claude/projects/p/memory/f.md"'))
        self.assertBlocked(self.bash("echo x > ${HOME}/code/repo/f.md"))

    def test_cd_tracked_for_relative_targets(self):
        self.assertAllowed(self.bash("cd " + SCRATCH + " && echo x > out.txt"))
        self.assertBlocked(self.bash("cd " + SCRATCH + " && cd " + REPO + " && echo x > out.txt"))
        # After "cd -" the cwd is unknown, so a relative target is unresolvable.
        self.assertBlocked(self.bash("cd " + SCRATCH + " && cd - && echo x > out.txt",
                                     cwd=SCRATCH))

    def test_tee(self):
        self.assertBlocked(self.bash("echo x | tee -a src/app.py"))
        self.assertAllowed(self.bash("make 2>&1 | tee " + SCRATCH + "/build.log"))

    def test_tee_to_devices_allowed(self):
        self.assertAllowed(self.bash("make 2>&1 | tee /dev/stderr | grep FAIL"))
        self.assertAllowed(self.bash("echo x | tee /dev/null"))

    def test_writes_behind_shell_keywords_blocked(self):
        for cmd in ("for f in src/*.py; do sed -i '' 's/a/b/' \"$f\"; done",
                    "if true; then cp " + SCRATCH + "/a src/b; fi",
                    "if false; then :; else mv src/a " + SCRATCH + "/; fi",
                    "while read f; do tee src/b; done < list",
                    "{ cp " + SCRATCH + "/a src/b; }",
                    "! cp " + SCRATCH + "/a src/b"):
            with self.subTest(cmd=cmd):
                self.assertBlocked(self.bash(cmd))
        self.assertAllowed(self.bash("for f in src/*.py; do wc -l \"$f\"; done"))

    def test_xargs_and_find_exec(self):
        self.assertBlocked(self.bash("grep -l foo src | xargs sed -i 's/a/b/'"))
        self.assertBlocked(self.bash("ls | xargs -0 -n 1 -I {} cp {} src/"))
        self.assertBlocked(self.bash("find src -name '*.py' -exec sed -i 's/a/b/' {} +"))
        self.assertBlocked(self.bash("find src -name '*.py' -exec sed -i 's/a/b/' {} \\;"))
        self.assertBlocked(self.bash("find src -execdir mv {} x \\;"))
        self.assertAllowed(self.bash("find src -name '*.py' -exec grep -n TODO {} +"))
        self.assertAllowed(self.bash("find src -name '*.py' -exec cp {} " + SCRATCH + "/ \\;"))
        self.assertAllowed(self.bash("git ls-files | xargs wc -l"))

    def test_sed_in_place_without_file_blocked(self):
        self.assertBlocked(self.bash("cat list | sed -i 's/a/b/'"))

    def test_shell_dash_c_analysed(self):
        self.assertBlocked(self.bash("sh -c 'echo x > src/app.py'"))
        self.assertBlocked(self.bash("bash -lc \"sed -i '' s/a/b/ src/app.py\""))
        self.assertBlocked(self.bash("zsh <<'EOF'\ncp " + SCRATCH + "/a src/b\nEOF"))
        self.assertAllowed(self.bash("bash -c 'ls > /dev/null'"))
        self.assertAllowed(self.bash("sh -c 'echo x > " + SCRATCH + "/f'"))

    def test_glob_inside_allowed_zone(self):
        self.assertAllowed(self.bash("mv " + SCRATCH + "/*.md " + SCRATCH + "/old/"))
        self.assertBlocked(self.bash("mv src/*.md " + SCRATCH + "/old/"))
        self.assertBlocked(self.bash("cp " + SCRATCH + "/a src/*.md"))
        # A glob in a folder name could reach anywhere: still unresolvable.
        self.assertBlocked(self.bash("mv " + SCRATCH + "/*/a.md " + SCRATCH + "/b.md"))
        # ".*" matches "..".
        self.assertBlocked(self.bash("mv " + SCRATCH + "/.* " + SCRATCH + "/old/"))
        # Brace expansion can hold a "/" or "..": unresolvable.
        self.assertBlocked(self.bash("cp a " + SCRATCH + "/{x,../../../../Users/testhome/f}"))

    def test_cp_mv(self):
        self.assertBlocked(self.bash("cp " + SCRATCH + "/draft.py src/app.py"))
        self.assertBlocked(self.bash("cp -t src " + SCRATCH + "/draft.py"))
        self.assertBlocked(self.bash("mv " + SCRATCH + "/draft.py " + REPO + "/src/"))
        # mv out of the repo deletes the source there.
        self.assertBlocked(self.bash("mv src/app.py " + SCRATCH + "/"))
        self.assertAllowed(self.bash("cp src/app.py " + SCRATCH + "/app.py.orig"))
        self.assertAllowed(self.bash("mv " + SCRATCH + "/a " + SCRATCH + "/b"))

    # --- Bash: python writes ----------------------------------------------

    def test_python_heredoc_writing_memory_allowed(self):
        script = (
            "python3 - <<'EOF'\n"
            "import os\n"
            "from pathlib import Path\n"
            "if 2 > 1:\n"
            "    Path(\"" + MEMORY + "/fact.md\").write_text(\"it's > ok\\n\")\n"
            "with open(os.path.expanduser('~/.claude/projects/p/memory/MEMORY.md'), 'a') as fh:\n"
            "    fh.write('- [Fact](fact.md)\\n')\n"
            "print(open('" + REPO + "/src/app.py').read())\n"
            "EOF"
        )
        self.assertAllowed(self.bash(script))

    def test_python_writes_to_repo_blocked(self):
        self.assertBlocked(self.bash(
            "python3 - <<'EOF'\nopen('" + REPO + "/src/app.py', 'w').write('x')\nEOF"))
        self.assertBlocked(self.bash(
            "python3 -c \"open('src/app.py', mode='r+').write('x')\""))
        self.assertBlocked(self.bash(
            "python3 - <<EOF\nfrom pathlib import Path\n"
            "Path('" + REPO + "/a.md').write_bytes(b'x')\nEOF"))
        # Quotes escaped for the shell are seen as Python sees them.
        self.assertBlocked(self.bash(
            'python3 -c "import pathlib; pathlib.Path(\\"src/a\\").open(\\"w\\").write(\\"a\\")"'))
        self.assertAllowed(self.bash(
            'python3 -c "import pathlib; pathlib.Path(\\"/tmp/claude-1/a\\").open(\\"w\\")"'))
        self.assertBlocked(self.bash("cd src && env PYTHONPATH=. python3 -c 'open(\"x\", \"a\")'"))
        # A bare "~" is not expanded by Python: it is a relative folder.
        self.assertBlocked(self.bash(
            "python3 -c \"open('~/.claude/projects/p/memory/f.md', 'w')\""))

    def test_python_mode_keyword_and_module_open(self):
        self.assertBlocked(self.bash(
            "python3 -c \"from pathlib import Path; Path('src/a').open(mode='w')\""))
        self.assertBlocked(self.bash("python3 -c \"import io; io.open('src/a', 'w')\""))
        self.assertBlocked(self.bash("python3 -c \"import os; os.open('src/a', os.O_WRONLY)\""))
        # A file name made of mode letters is not a mode.
        self.assertAllowed(self.bash("python3 -c \"import io; print(io.open('a').read())\""))
        # open( in a comment or a string is not a call.
        self.assertAllowed(self.bash(
            "python3 - <<'EOF'\n# open('src/a', 'w')\nprint(\"open('src/a', 'w')\")\nEOF"))

    def test_python_judged_with_its_own_cwd(self):
        self.assertBlocked(self.bash("python3 -c \"open('a.md', 'w')\"; cd " + SCRATCH))
        self.assertAllowed(self.bash(
            "cd " + SCRATCH + " && python3 -c \"open('a', 'w')\" && cd -"))
        self.assertAllowed(self.bash(
            "cd " + SCRATCH + " && python3 - <<'EOF' && cd -\nopen('a', 'w')\nEOF"))

    def test_heredoc_body_belongs_to_its_command(self):
        # The brief is not python even though python runs on the same line.
        self.assertAllowed(self.bash(
            "cat > " + SCRATCH + "/brief.md <<'EOF'\nthen open('src/a', 'w')\nEOF\n"
            "python3 -c 'print(1)'"))
        self.assertBlocked(self.bash(
            "cat > " + SCRATCH + "/brief.md <<'EOF'\nok\nEOF\n"
            "python3 - <<'EOF'\nopen('src/a', 'w')\nEOF"))
        # Stdin of a script file is data, not code.
        self.assertAllowed(self.bash("python3 tool.py <<'EOF'\nopen('src/a', 'w')\nEOF"))
        self.assertAllowed(self.bash("bash run.sh <<'EOF'\ncat a > src/b\nEOF"))
        self.assertAllowed(self.bash(
            "python3 -c \"import webbrowser; webbrowser.open('http://example.com')\""))

    def test_python_not_parseable(self):
        self.assertBlocked(self.bash("python3 - <<'EOF'\nopen('src/a', 'w'\nEOF"))
        self.assertAllowed(self.bash("python3 - <<'EOF'\nprint(1\nEOF"))

    def test_python_unresolvable_target_blocked(self):
        self.assertBlocked(self.bash(
            "python3 - <<'EOF'\nimport sys\nopen(sys.argv[1], 'w').write('x')\nEOF"))
        self.assertBlocked(self.bash(
            "python3 - <<'EOF'\np = make_path()\np.write_text('x')\nEOF"))

    def test_python_reads_allowed(self):
        self.assertAllowed(self.bash(
            "python3 - <<'EOF'\nimport json\nprint(json.load(open('package.json')))\nEOF"))
        self.assertAllowed(self.bash("python3 -m json.tool < data.json"))

    def test_non_python_heredoc_body_not_scanned_as_shell(self):
        self.assertAllowed(self.bash(
            "cat > " + SCRATCH + "/brief.md <<'EOF'\n"
            "Run: cat a > src/app.py, then sed -i x f and l'autre\nEOF"))
        self.assertAllowed(self.bash(
            "gh issue comment 12 --body \"$(cat <<'EOF'\nresult > expected\nEOF\n)\""))

    # --- reads and tooling stay open -------------------------------------

    def test_reads_git_gh_orca_allowed(self):
        for cmd in ("git status", "git diff --stat main...HEAD", "gh issue list --limit 20",
                    "gh pr view 42 --json title,body", "orca terminal read --terminal t1",
                    "rg -n 'TODO' src | head -20", "cat src/app.py",
                    "ls -la " + HOME + "/.claude/hooks"):
            with self.subTest(cmd=cmd):
                self.assertAllowed(self.bash(cmd))

    # --- the hook install exception --------------------------------------

    def test_install_reviewed_hook_allowed(self):
        self.assertAllowed(self.bash("cp " + STAGING + "/guard_coordinator.py ~/.claude/hooks/"))
        self.assertAllowed(self.bash(
            "cp -p " + STAGING + "/guard_coordinator.py " + STAGING + "/test_guard_coordinator.py "
            + HOME + "/.claude/hooks/"))
        self.assertAllowed(self.bash(
            "cp /tmp/claude-501/x/hooks-staging/guard_coordinator.py "
            "$HOME/.claude/hooks/guard_coordinator.py"))
        self.assertAllowed(self.bash("cd " + STAGING + " && cp guard_coordinator.py ~/.claude/hooks/"))
        self.assertAllowed(self.bash("cp " + STAGING + "/*.py ~/.claude/hooks/"))
        self.assertAllowed(self.bash("cp -t ~/.claude/hooks " + STAGING + "/guard_coordinator.py"))

    def test_install_exception_is_narrow(self):
        # Source outside a hooks-staging folder.
        self.assertBlocked(self.bash("cp " + SCRATCH + "/guard.py ~/.claude/hooks/"))
        self.assertBlocked(self.bash("cp " + REPO + "/hooks-staging/guard.py ~/.claude/hooks/"))
        # Destination other than ~/.claude/hooks/.
        self.assertBlocked(self.bash("cp " + STAGING + "/settings-entry.json ~/.claude/settings.json"))
        self.assertBlocked(self.bash("cp " + STAGING + "/g.py ~/.claude/hooks/sub/g.py"))
        # Only cp: mv, redirections and Write stay refused.
        self.assertBlocked(self.bash("mv " + STAGING + "/g.py ~/.claude/hooks/"))
        self.assertBlocked(self.bash("cat " + STAGING + "/g.py > ~/.claude/hooks/g.py"))
        self.assertBlocked(self.bash("cp " + STAGING + "/../evil.py ~/.claude/hooks/"))

    # --- robustness ------------------------------------------------------

    def test_invalid_input_does_not_crash(self):
        for raw in ("{not json", "", "[]", json.dumps({"tool_name": "Edit"}),
                    json.dumps({"tool_name": "Bash", "tool_input": {"command": None}}),
                    json.dumps({"tool_name": ["Bash"], "tool_input": {"command": "ls"}})):
            with self.subTest(raw=raw):
                self.assertAllowed(raw)
        # A non-string cwd is unknown: a relative target is refused, no crash.
        self.assertBlocked(self.bash("echo x > a.md", cwd=42))

    def test_unbalanced_quotes(self):
        self.assertAllowed(self.bash("echo 'unterminated"))
        self.assertBlocked(self.bash("echo 'x > src/app.py"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
