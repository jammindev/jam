#!/usr/bin/env python3
"""Tests for session_start_recap.py — the Orca block and the method line.

Each case runs the hook the way Claude Code does: a JSON payload on stdin, the
recap read on stdout. Calling the functions directly would test the helpers and
not the hook. The Orca CLI is replaced by a fake binary generated in a temp
folder and wired in through JAM_ORCA_BIN, or through the PATH for the case
that finds it there, so the cases never depend on Orca running. HOME points
at the temp folder too, so the hook never touches the real ~/.claude.

The fake only answers the exact calls the hook is meant to make
(`worktree show|terminal list --worktree id:<ID> --json`); anything else, such as
`worktree current` which resolves from the cwd, exits non-zero. It also logs the
start and end of every call, so "silence outside Orca" is asserted on the CLI
too, and the two calls can be shown to overlap in time.

Its terminal rows copy the real `orca terminal list --json` output: handle,
title, worktreeId, connected, preview…, and agentIdentity set to "claude" for an
agent terminal, absent for a plain shell.

Run: python3 -m unittest hooks.test_session_start_recap
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "session_start_recap.py")
PLUGIN = os.path.dirname(HERE)
SCRIPTS = os.path.join(PLUGIN, "scripts")
# The method line names the process and profiles of the plugin running the
# hook, as absolute paths: never the copies a project may hold in its worktree.
METHOD_LINE = (f"Méthode : fiche `docs/methode.md` · process "
               f"`{os.path.join(PLUGIN, 'process', 'README.md')}` · profils "
               f"`{os.path.join(PLUGIN, 'roles')}/`\n")

# Runs the hook with orca_cli.APP_BIN replaced, so "no Orca anywhere" can be
# tested on a machine where the Orca app is installed. The hook imports the
# same orca_cli module, already loaded and patched.
WITH_APP_BIN = (
    "import runpy, sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "import orca_cli\n"
    "orca_cli.APP_BIN = sys.argv[2]\n"
    "hook = sys.argv[3]\n"
    "sys.argv = [hook]\n"
    "runpy.run_path(hook, run_name='__main__')\n"
)

# Runs the hook with its ORCA_TIMEOUT replaced. The fake CLI is a Python
# script: on a loaded CI runner, its start-up alone can eat the hook's one
# second. The cases that wait for an answer give it RESPONSE_TIMEOUT; the
# slowness cases keep the real delay.
WITH_TIMEOUT = (
    "import sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "import session_start_recap as hook\n"
    "assert isinstance(hook.ORCA_TIMEOUT, (int, float))\n"
    "hook.ORCA_TIMEOUT = float(sys.argv[2])\n"
    "hook.main()\n"
)
RESPONSE_TIMEOUT = 5
REAL_TIMEOUT = 1

# Shaped like the real `<repo-id>::<absolute path>` and longer than the
# 120-char cap on displayed text: an identifier must reach the CLI untouched.
WORKTREE_ID = ("0f8e2c1a-1111-2222-3333-444455556666::/Users/x/orca/workspaces/jam/"
               + "nom-de-worktree-tres-long-" * 4)
# Same for the handle, with a double space that text flattening would squash.
SELF_HANDLE = "term-self  " + "h" * 120
SECRET = "orca-secret-token-do-not-print"
PREVIEW = "preview-text-do-not-print"
NOT_IDENTIFIED = "terminal(aux) avec agent dans ce worktree (terminal courant non identifié)"
UNVERIFIED = "Autres agents : liste des terminaux indisponible (non vérifié)\n"

FAKE_ORCA = r'''#!@PYTHON@
import json, os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]

def log(event):
    with open(os.path.join(here, "calls.log"), "a") as fh:
        fh.write(json.dumps({"event": event, "at": time.time(), "args": args}) + "\n")

log("start")
with open(os.path.join(here, "spec.json")) as fh:
    spec = json.load(fh)
target = ["--worktree", "id:" + spec["worktree_id"], "--json"]
if args == ["worktree", "show"] + target:
    command = "show"
elif args == ["terminal", "list"] + target:
    command = "list"
else:
    sys.stderr.write("unexpected call: %r\n" % (args,))
    sys.exit(2)
time.sleep(spec["delay"])
if command in spec["fail"]:
    sys.stderr.write("orca: app not running\n")
    sys.exit(1)
if spec["garbage"]:
    print("{ this is not json")
elif command in spec["raw"]:
    print(json.dumps(spec["raw"][command]))
elif command == "show":
    print(json.dumps({"ok": True, "token": spec["token"],
                      "result": {"worktree": spec["worktree"]}}))
else:
    print(json.dumps({"ok": True, "result": {
        "terminals": spec["terminals"], "totalCount": len(spec["terminals"])
        if isinstance(spec["terminals"], list) else 0, "truncated": False}}))
log("end")
'''

def terminal(handle, title, agent=None, connected=True):
    """One row shaped like the real `orca terminal list --json` output."""
    row = {"handle": handle, "ptyId": f"{WORKTREE_ID}@@{handle}",
           "worktreeId": WORKTREE_ID, "worktreePath": "/tmp/wt", "branch": "",
           "title": title, "connected": connected, "writable": True,
           "preview": PREVIEW, "executionHostId": "local"}
    if agent:
        row["agentIdentity"] = agent
    return row


class SessionStartRecapTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="session-start-recap-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.plain = self.make_repo("plain")
        self.with_method = self.make_repo("with-method", with_method=True)

    # --- fixtures --------------------------------------------------------

    def make_repo(self, name, with_method=False, own_process=True):
        path = os.path.join(self.root, name)
        os.makedirs(path)
        # Isolated HOME: no personal init.templateDir or hooks in test repos.
        subprocess.run(["git", "init", "-q", path], capture_output=True,
                       env=self.base_env(), check=True)
        if with_method:
            self.write(path, "docs/methode.md", "# Fiche\n")
        if own_process:
            # Copies of the method inside a project (jam holds one): the hook
            # must never point at them, whether the repo has a fiche or not.
            self.write(path, "process/README.md", "# Copie\n")
            self.write(path, "docs/process/README.md", "# Ancien\n")
        return path

    def write(self, repo, relative, content):
        target = os.path.join(repo, relative)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as fh:
            fh.write(content)

    def make_fake(self, name, worktree=None, terminals=None, fail=(), delay=0,
                  garbage=False, raw=None):
        folder = os.path.join(self.root, name)
        os.makedirs(folder)
        with open(os.path.join(folder, "spec.json"), "w") as fh:
            json.dump({"worktree_id": WORKTREE_ID, "token": SECRET,
                       "worktree": {} if worktree is None else worktree,
                       "terminals": [] if terminals is None else terminals,
                       "fail": list(fail), "delay": delay, "garbage": garbage,
                       "raw": raw or {}}, fh)
        binary = os.path.join(folder, "orca")
        with open(binary, "w") as fh:
            fh.write(FAKE_ORCA.replace("@PYTHON@", sys.executable))
        os.chmod(binary, 0o755)
        return binary

    def fake_calls(self, binary):
        try:
            with open(os.path.join(os.path.dirname(binary), "calls.log")) as fh:
                return [json.loads(line) for line in fh]
        except FileNotFoundError:
            return []

    def base_env(self):
        # The suite may itself run inside Orca: drop the real context so it
        # cannot leak into the "outside Orca" cases. HOME isolates ~/.claude;
        # the ceiling keeps git from finding a repo above the temp folder.
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("ORCA_", "JAM_"))}
        env["HOME"] = self.root
        env["GIT_CEILING_DIRECTORIES"] = self.root
        return env

    def orca_env(self, binary, role=None, handle=SELF_HANDLE):
        env = self.base_env()
        env.update({"JAM_ORCA_BIN": binary, "ORCA_WORKTREE_ID": WORKTREE_ID,
                    "ORCA_AUTH_TOKEN": SECRET})
        if handle is not None:
            env["ORCA_TERMINAL_HANDLE"] = handle
        if role:
            env["JAM_ROLE"] = role
        return env

    def run_hook(self, cwd, env, orca_timeout=RESPONSE_TIMEOUT, process_cwd=None):
        started = time.monotonic()
        done = subprocess.run(
            [sys.executable, "-c", WITH_TIMEOUT, HERE, str(orca_timeout)],
            input=json.dumps({"cwd": cwd}), capture_output=True, text=True,
            env=env, cwd=process_cwd, timeout=60,
        )
        self.elapsed = time.monotonic() - started
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn("Traceback", done.stderr)
        return done.stdout

    # --- outside Orca: total silence, CLI never touched -------------------

    def test_outside_orca(self):
        idle = self.make_fake("idle")
        env = self.base_env()
        env["JAM_ORCA_BIN"] = idle
        env["JAM_ROLE"] = "IMPLÉMENTEUR"  # a role alone does not mean Orca
        out = self.run_hook(self.plain, env)
        self.assertTrue(out.startswith("[jam] Reprise de contexte"), out)
        self.assertNotIn("## Orca", out)
        self.assertNotIn("Méthode", out)
        self.assertNotIn("Process du repo", out)
        self.assertNotIn("toujours --json", out)
        self.assertEqual(self.fake_calls(idle), [])

    def test_blank_worktree_id_is_outside_orca(self):
        idle = self.make_fake("idle")
        env = self.orca_env(idle)
        env["ORCA_WORKTREE_ID"] = "   "
        out = self.run_hook(self.plain, env)
        self.assertIn("[jam] Reprise de contexte", out)
        self.assertNotIn("## Orca", out)
        self.assertEqual(self.fake_calls(idle), [])

    def test_method_line_outside_orca(self):
        # From a subfolder: the fiche is looked up at the repo root, not the cwd.
        sub = os.path.join(self.with_method, "src", "deep")
        os.makedirs(sub)
        out = self.run_hook(sub, self.base_env())
        self.assertIn("\n" + METHOD_LINE, out)
        self.assertEqual(out.count("Méthode"), 1)
        # The repo's own process/ and docs/process/ are never named.
        self.assertNotIn(os.path.join(self.with_method, "process"), out)
        self.assertNotIn("Process du repo", out)
        self.assertNotIn("## Orca", out)

    def test_no_fiche_no_method_line(self):
        # A repo with copies of the process but no fiche does not follow the
        # method: no line, rather than a pointer it would not use.
        out = self.run_hook(self.plain, self.base_env())
        self.assertIn("[jam] Reprise de contexte", out)
        self.assertNotIn("Méthode", out)
        self.assertNotIn("process", out)

    def test_fiche_that_is_a_folder_is_no_fiche(self):
        repo = self.make_repo("fiche-folder", own_process=False)
        os.makedirs(os.path.join(repo, "docs", "methode.md"))
        out = self.run_hook(repo, self.base_env())
        self.assertNotIn("Méthode", out)

    # --- inside Orca ------------------------------------------------------

    def test_with_role(self):
        fake = self.make_fake("full", worktree={
            "displayName": "bristlemouth",
            "workspaceStatus": "in-progress",
            "comment": "R-004 contexte Orca",
            "linkedIssue": 42,
            "linkedPR": 7,
        }, terminals=[
            terminal(SELF_HANDLE, "Implémenteur", "claude"),
            terminal("term-shell", "zsh"),  # no agent: no warning
        ])
        out = self.run_hook(self.plain, self.orca_env(fake, role="IMPLÉMENTEUR"))
        self.assertIn("\n\n## Orca\n\n", out)
        self.assertNotIn("\n\n\n", out)
        self.assertIn("Worktree `bristlemouth` · carte in-progress "
                      "« R-004 contexte Orca » · issue #42 · PR #7\n", out)
        self.assertIn("Ce terminal : « Implémenteur » · rôle : IMPLÉMENTEUR\n", out)
        self.assertIn(f"`{fake}`", out)
        self.assertIn("toujours --json", out)
        self.assertIn("doc : orca skills get orca-cli", out)
        self.assertNotIn("⚠", out)
        self.assertNotIn(NOT_IDENTIFIED, out)
        self.assertNotIn("session libre", out)
        self.assertNotIn(UNVERIFIED, out)
        self.assertNotIn(SECRET, out)
        self.assertNotIn(WORKTREE_ID, out)
        self.assertNotIn(PREVIEW, out)

    def test_free_session_other_agent_omitted_parts(self):
        fake = self.make_fake("sparse", worktree={
            "displayName": "jam",
            "workspaceStatus": "",
            "linkedIssue": 12,
            "linkedPR": None,
        }, terminals=[
            terminal(SELF_HANDLE, "Moi", "claude"),
            terminal("term-b", "Relecteur", "claude"),
            terminal("term-c", "Shell vide"),
            terminal("term-d", "Testeur", "claude"),
        ])
        out = self.run_hook(self.with_method, self.orca_env(fake))
        self.assertIn("Worktree `jam` · issue #12\n", out)
        self.assertIn("Ce terminal : « Moi » · session libre (sans rôle) : "
                      "ne pas écrire là où un rôle travaille\n", out)
        self.assertIn("⚠ Autre agent actif dans ce worktree : « Relecteur »\n", out)
        self.assertIn("⚠ Autre agent actif dans ce worktree : « Testeur »\n", out)
        self.assertIn(METHOD_LINE, out)
        self.assertNotIn("carte", out)
        self.assertNotIn("PR #", out)
        self.assertNotIn("Shell vide", out)
        self.assertNotIn("rôle : ", out)
        self.assertNotIn("dans ce worktree : « Moi »", out)
        self.assertNotIn(NOT_IDENTIFIED, out)

    def test_current_terminal_not_identified(self):
        # Orca shells can lose their handle or keep a stale one: then nobody
        # may be named as "another agent", since it could be this very one.
        rows = [terminal(SELF_HANDLE, "Moi", "claude"),
                terminal("term-b", "Relecteur", "claude"),
                terminal("term-c", "zsh")]
        for label, handle in (("absent", None), ("empty", ""),
                              ("blank", "  "), ("stale", "term-gone")):
            with self.subTest(handle=label):
                fake = self.make_fake(f"unidentified-{label}", worktree={
                    "displayName": "jam"}, terminals=rows)
                out = self.run_hook(self.plain, self.orca_env(
                    fake, role="TESTEUR", handle=handle))
                self.assertIn(f"\n2 {NOT_IDENTIFIED}\n", out)
                self.assertIn("\nCe terminal · rôle : TESTEUR\n", out)
                self.assertNotIn("⚠", out)
                self.assertNotIn("Moi", out)
                self.assertNotIn("Relecteur", out)

    def test_disconnected_agent_ignored(self):
        # A disconnected terminal may keep agentIdentity: it is not a live
        # agent. A row without the field still counts, to stay on the safe side.
        no_field = terminal("term-c", "Sans champ", "claude")
        del no_field["connected"]
        rows = [terminal(SELF_HANDLE, "Moi", "claude"),
                terminal("term-b", "Fantôme", "claude", connected=False),
                no_field]
        fake = self.make_fake("disconnected", worktree={"displayName": "jam"},
                              terminals=rows)
        out = self.run_hook(self.plain, self.orca_env(fake))
        self.assertIn("⚠ Autre agent actif dans ce worktree : « Sans champ »\n", out)
        self.assertNotIn("Fantôme", out)
        self.assertEqual(out.count("⚠"), 1)

        fake = self.make_fake("disconnected-unidentified",
                              worktree={"displayName": "jam"}, terminals=rows)
        out = self.run_hook(self.plain, self.orca_env(fake, handle="term-gone"))
        self.assertIn(f"\n2 {NOT_IDENTIFIED}\n", out)

    def test_linked_refs_only_positive_ints(self):
        # Orca's contract: linkedIssue / linkedPR are a number or null.
        for i, value in enumerate(("12", "#12", "https://x.test/issues/9#issuecomment-123",
                                   {"number": 7}, 0, -3, True, 4.0, [5])):
            with self.subTest(value=value):
                fake = self.make_fake(f"ref-{i}", worktree={
                    "displayName": "jam", "linkedIssue": value, "linkedPR": value})
                out = self.run_hook(self.plain, self.orca_env(fake))
                self.assertIn("Worktree `jam`\n", out)
                self.assertNotIn("#", out.split("## Orca", 1)[1])

    def test_free_text_flattened_and_capped(self):
        long_title = "Titre\n" + "x" * 200
        fake = self.make_fake("messy", worktree={
            "displayName": "jam\n  bis",
            "workspaceStatus": "in-progress",
            "comment": "ligne 1\nligne 2\n\n\tligne 3",
        }, terminals=[
            terminal(SELF_HANDLE, long_title, "claude"),
            terminal("term-b", "Autre\r\nagent", "claude"),
        ])
        out = self.run_hook(self.plain, self.orca_env(fake, role=" IMPLÉ\nMENTEUR "))
        capped = ("Titre " + "x" * 200)[:120]
        self.assertIn("Worktree `jam bis` · carte in-progress "
                      "« ligne 1 ligne 2 ligne 3 »\n", out)
        self.assertIn(f"Ce terminal : « {capped} » · rôle : IMPLÉ MENTEUR\n", out)
        self.assertIn("⚠ Autre agent actif dans ce worktree : « Autre agent »\n", out)
        self.assertNotIn("x" * 121, out)
        self.assertNotIn("\n\n\n", out)

    def test_orca_block_outside_git_repo(self):
        outside = os.path.join(self.root, "not-a-repo")
        os.makedirs(outside)
        fake = self.make_fake("nogit", worktree={"displayName": "jam"},
                              terminals=[terminal(SELF_HANDLE, "Moi", "claude")])
        out = self.run_hook(outside, self.orca_env(fake, role="TESTEUR"))
        self.assertTrue(out.startswith(
            "[jam] Reprise de contexte (hook SessionStart)\n\n## Orca\n\n"
            "Worktree `jam`\nCe terminal : « Moi » · rôle : TESTEUR\n"), out)
        self.assertNotIn("**Worktree**", out)
        self.assertNotIn("\n\n\n", out)

    # --- the CLI misbehaves: degrade, never block, never crash ------------

    def test_cli_fails(self):
        fake = self.make_fake("failing", fail=("show", "list"))
        out = self.run_hook(self.plain, self.orca_env(fake, role="TESTEUR"))
        self.assertIn("[jam] Reprise de contexte", out)
        self.assertIn("## Orca", out)
        self.assertIn("indisponible", out)
        self.assertIn(UNVERIFIED, out)
        self.assertIn("rôle : TESTEUR", out)
        self.assertNotIn("app not running", out)
        self.assertNotIn("⚠", out)

    def test_show_ok_list_fails(self):
        # No terminal list: "no other agent" and "could not check" must differ.
        fake = self.make_fake("list-fails", fail=("list",), worktree={
            "displayName": "jam", "workspaceStatus": "in-progress"})
        out = self.run_hook(self.plain, self.orca_env(fake, role="TESTEUR"))
        self.assertIn("Worktree `jam` · carte in-progress\n", out)
        self.assertIn("\nCe terminal · rôle : TESTEUR\n", out)
        self.assertIn(UNVERIFIED, out)
        self.assertNotIn("détails indisponibles", out)
        self.assertNotIn("app not running", out)
        self.assertNotIn("⚠", out)
        self.assertNotIn(NOT_IDENTIFIED, out)

    def test_cli_too_slow(self):
        # The real one-second delay, against a CLI that never answers in time.
        fake = self.make_fake("slow", delay=5)
        out = self.run_hook(self.plain, self.orca_env(fake), orca_timeout=REAL_TIMEOUT)
        # The two calls run in parallel: the hook costs one delay plus its own
        # start-up, where two sequential calls would cost two delays and more.
        self.assertLess(self.elapsed, 2 * REAL_TIMEOUT)
        self.assertIn("## Orca", out)
        self.assertIn("indisponible", out)
        self.assertIn(UNVERIFIED, out)
        self.assertIn("session libre", out)

    def test_cli_calls_overlap(self):
        # Both calls must answer here, so the default RESPONSE_TIMEOUT applies:
        # the overlap is read from the fake's log, not from a deadline.
        fake = self.make_fake("overlap", delay=0.5, worktree={"displayName": "jam"},
                              terminals=[terminal(SELF_HANDLE, "Moi", "claude")])
        out = self.run_hook(self.plain, self.orca_env(fake))
        self.assertIn("Worktree `jam`\n", out)
        self.assertIn("Ce terminal : « Moi »", out)
        calls = self.fake_calls(fake)
        starts = [c["at"] for c in calls if c["event"] == "start"]
        ends = [c["at"] for c in calls if c["event"] == "end"]
        self.assertEqual((len(starts), len(ends)), (2, 2), calls)
        # Both calls started before either finished: they ran in parallel.
        self.assertLess(max(starts), min(ends))

    def test_cli_missing(self):
        missing = os.path.join(self.root, "nowhere", "orca")
        out = self.run_hook(self.plain, self.orca_env(missing, role="TESTEUR"))
        self.assertIn("## Orca", out)
        self.assertIn("introuvable", out)
        self.assertIn("rôle : TESTEUR", out)
        self.assertNotIn("toujours --json", out)
        # The cause is "missing", not "failing or too slow"; nothing was listed.
        self.assertNotIn("trop lente", out)
        self.assertNotIn(UNVERIFIED, out)

    def test_cli_found_on_path(self):
        fake = self.make_fake("on-path", worktree={"displayName": "jam"},
                              terminals=[terminal(SELF_HANDLE, "Moi", "claude")])
        env = self.orca_env(fake)
        del env["JAM_ORCA_BIN"]
        env["PATH"] = os.path.dirname(fake) + os.pathsep + env.get("PATH", os.defpath)
        out = self.run_hook(self.plain, env)
        self.assertIn("Worktree `jam`\n", out)
        self.assertIn("Ce terminal : « Moi »", out)
        self.assertIn(f"`{fake}`", out)

    def test_cli_missing_everywhere(self):
        # No JAM_ORCA_BIN, no orca on the PATH (only git's folder), and the
        # app's standard location replaced by a path that does not exist.
        missing_app = os.path.join(self.root, "no-app", "orca")
        env = self.orca_env(missing_app, role="TESTEUR")
        del env["JAM_ORCA_BIN"]
        env["PATH"] = os.path.dirname(shutil.which("git"))
        done = subprocess.run(
            [sys.executable, "-c", WITH_APP_BIN, SCRIPTS, missing_app, HOOK],
            input=json.dumps({"cwd": self.plain}),
            capture_output=True, text=True, env=env, timeout=30,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        out = done.stdout
        self.assertTrue(out.startswith("[jam] Reprise de contexte"), out)
        self.assertIn("rôle : TESTEUR", out)
        line = next((l for l in out.splitlines() if "CLI Orca introuvable" in l), None)
        self.assertIsNotNone(line, out)
        # No path in the message: not the replaced location, not the real one.
        self.assertNotIn("/", line)
        self.assertNotIn(missing_app, out)
        self.assertNotIn("toujours --json", out)

    def test_runs_from_any_cwd(self):
        # Claude Code starts the hook from the session's folder: the hook finds
        # scripts/orca_cli.py from its own location, never from the cwd (here a
        # temp folder, first on sys.path, with no orca_cli in it).
        fake = self.make_fake("any-cwd", worktree={"displayName": "jam"})
        out = self.run_hook(self.plain, self.orca_env(fake), process_cwd=self.root)
        self.assertIn("Worktree `jam`\n", out)

    def test_invalid_json(self):
        fake = self.make_fake("garbage", garbage=True)
        out = self.run_hook(self.plain, self.orca_env(fake))
        self.assertIn("## Orca", out)
        self.assertIn("indisponible", out)
        self.assertIn(UNVERIFIED, out)
        self.assertNotIn("⚠", out)

    def test_unexpected_json_shapes(self):
        # Valid JSON, wrong shape: degrade like a failure, never crash.
        cases = {
            "result-list": dict(raw={"show": {"result": []}, "list": {"result": []}}),
            "top-level-list": dict(raw={"show": [1, 2], "list": "terminals"}),
            "worktree-string": dict(worktree="bristlemouth",
                                    terminals={"handle": SELF_HANDLE, "title": "Moi"}),
            "worktree-null": dict(raw={"show": {"ok": True, "result": {"worktree": None}},
                                       "list": {"ok": True, "result": {"terminals": None}}}),
        }
        for label, spec in cases.items():
            with self.subTest(shape=label):
                fake = self.make_fake(f"shape-{label}", **spec)
                out = self.run_hook(self.plain, self.orca_env(fake))
                self.assertIn("## Orca", out)
                self.assertIn("détails indisponibles", out)
                self.assertIn(UNVERIFIED, out)
                self.assertIn("\nCe terminal · session libre", out)
                self.assertNotIn("⚠", out)
                self.assertNotIn(NOT_IDENTIFIED, out)

    def test_terminal_rows_not_objects(self):
        fake = self.make_fake("odd-rows", worktree={"displayName": "jam"}, terminals=[
            "zsh", 3, None, ["term-b", "claude"],
            terminal(SELF_HANDLE, "Moi", "claude"),
            terminal("term-b", "Relecteur", "claude"),
        ])
        out = self.run_hook(self.plain, self.orca_env(fake))
        self.assertIn("Ce terminal : « Moi »", out)
        self.assertIn("⚠ Autre agent actif dans ce worktree : « Relecteur »\n", out)
        self.assertEqual(out.count("⚠"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
