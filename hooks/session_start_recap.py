#!/usr/bin/env python3
"""SessionStart hook: print a compact recap so a new session starts with the
git state already in context.

Inside Orca (ORCA_WORKTREE_ID set), an extra block tells the agent which
worktree, card and terminal it runs in, read from the Orca CLI through the
plugin's scripts/orca_cli.py.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# scripts/ is found from this file, not from the cwd: Claude Code runs the hook
# from the session's folder, anywhere on the machine.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
import orca_cli  # noqa: E402

REPO_PROCESS = "docs/process/README.md"
# Seconds per Orca call: the recap must never hold the session start hostage
# to a hung or absent Orca app. A module constant so the tests can raise it.
ORCA_TIMEOUT = 1


def git(cwd, *args, timeout=3):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True, text=True, timeout=timeout,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def orca_json(binary, *args):
    """Return the CLI's `result` object, or None on any failure (ORCA_TIMEOUT max)."""
    try:
        return orca_cli.call(*args, timeout=ORCA_TIMEOUT, binary=binary)
    except Exception:
        return None


def ref_number(value):
    """linkedIssue / linkedPR are a number or null in Orca's contract."""
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return None


def text(value):
    """One line, 120 chars max: comments and terminal titles are free text.

    Display only: identifiers sent to the CLI or compared must stay intact.
    """
    return " ".join(value.split())[:120] if isinstance(value, str) else ""


def orca_lines():
    """The `## Orca` block, or [] outside Orca (total silence there)."""
    # `<repo-id>::<absolute path>`: easily over 120 chars, never flatten it.
    worktree_id = (os.environ.get("ORCA_WORKTREE_ID") or "").strip()
    if not worktree_id:
        return []

    # By id, never `orca worktree current`: that one resolves from the cwd,
    # which may sit outside the worktree the terminal belongs to.
    target = ("--worktree", f"id:{worktree_id}")
    binary = orca_cli.find_binary()
    available = binary is not None
    show = terminals = None
    if available:
        # Both calls in parallel, so a hung CLI costs one second, not two.
        with ThreadPoolExecutor(max_workers=2) as pool:
            show_f = pool.submit(orca_json, binary, "worktree", "show", *target)
            term_f = pool.submit(orca_json, binary, "terminal", "list", *target)
            show, terminals = show_f.result(), term_f.result()

    lines = ["## Orca", ""]

    worktree = (show or {}).get("worktree")
    if isinstance(worktree, dict):
        name = text(worktree.get("displayName"))
        parts = [f"Worktree `{name}`" if name else "Worktree Orca"]
        status, comment = text(worktree.get("workspaceStatus")), text(worktree.get("comment"))
        if status or comment:
            card = " ".join(p for p in ("carte", status, comment and f"« {comment} »") if p)
            parts.append(card)
        issue, pr = ref_number(worktree.get("linkedIssue")), ref_number(worktree.get("linkedPR"))
        if issue:
            parts.append(f"issue #{issue}")
        if pr:
            parts.append(f"PR #{pr}")
        lines.append(" · ".join(parts))
    else:
        # A missing CLI gets its own line below: no misleading cause here.
        lines.append("Worktree Orca : détails indisponibles"
                     + (" (CLI en échec ou trop lente)" if available else ""))

    handle = (os.environ.get("ORCA_TERMINAL_HANDLE") or "").strip()
    rows = (terminals or {}).get("terminals")
    listed = isinstance(rows, list)
    rows = [t for t in rows if isinstance(t, dict)] if listed else []
    mine = next((t for t in rows if handle and t.get("handle") == handle), None)
    # The real CLI sets agentIdentity to "claude" on agent terminals and
    # leaves it out on plain shells. A disconnected terminal is no live agent;
    # a row without the field still counts, to stay on the safe side.
    agents = [t for t in rows if text(t.get("agentIdentity"))
              and t.get("connected") is not False]
    title = text((mine or {}).get("title"))
    role = text(os.environ.get("JAM_ROLE"))
    lines.append(
        (f"Ce terminal : « {title} »" if title else "Ce terminal")
        + (f" · rôle : {role}" if role else
           " · session libre (sans rôle) : ne pas écrire là où un rôle travaille")
    )

    # The collision to flag: two agents writing in the same worktree. Orca
    # shells can lose their handle or keep a stale one: without knowing which
    # row is ours, naming "another agent" could name this very terminal.
    if available and not listed:
        # Silence here would read as "no other agent" when nothing was checked.
        lines.append("Autres agents : liste des terminaux indisponible (non vérifié)")
    elif mine is None:
        if agents:
            lines.append(f"{len(agents)} terminal(aux) avec agent dans ce worktree "
                         "(terminal courant non identifié)")
    else:
        for t in agents:
            if t is not mine:
                lines.append("⚠ Autre agent actif dans ce worktree : "
                             f"« {text(t.get('title')) or '(sans titre)'} »")

    if available:
        lines.append(f"CLI Orca : `{binary}` (chemin complet, toujours --json) "
                     "· doc : orca skills get orca-cli")
    else:
        lines.append(orca_cli.NOT_FOUND)
    return lines


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    cwd = data.get("cwd") or os.getcwd()
    toplevel = git(cwd, "rev-parse", "--show-toplevel")
    try:
        orca = orca_lines()
    except Exception:
        orca = []  # never let the Orca block take the git recap down with it
    if not toplevel and not orca:
        sys.exit(0)

    # Every message of the plugin starts with [jam], to tell it from the hooks
    # a machine may still run on its own.
    lines = ["[jam] Reprise de contexte (hook SessionStart)", ""]

    if toplevel:
        branch = git(cwd, "branch", "--show-current") or "(HEAD détachée)"
        status = git(cwd, "status", "--porcelain")
        dirty = len([x for x in status.splitlines() if x.strip()])
        lines.append(f"**Worktree** `{os.path.basename(toplevel)}` · "
                     f"**branche** `{branch}` · {dirty} fichier(s) non commité(s)")
        if os.path.isfile(os.path.join(toplevel, REPO_PROCESS)):
            lines.append(f"Process du repo : `{REPO_PROCESS}`")

        log = git(cwd, "log", "--oneline", "-5", "--no-decorate")
        if log:
            lines.append("")
            lines.append("**5 derniers commits**")
            for line in log.splitlines():
                lines.append(f"- {line}")

        worktrees = git(cwd, "worktree", "list")
        others = [w for w in worktrees.splitlines()[1:] if w.strip()]
        if others:
            lines.append("")
            lines.append(f"**{len(others)} worktree(s) secondaire(s) actif(s)**")
            for w in others[:8]:
                path = w.split()[0]
                wb = w.split("[")[-1].rstrip("]") if "[" in w else "?"
                lines.append(f"- `{os.path.basename(path)}` → `{wb}`")

    if orca:
        if toplevel:
            lines.append("")  # the header already ends with a blank line
        lines.extend(orca)

    lines.append("")
    lines.append("_Ne relis pas cet état, il est déjà à jour. "
                 "Utilise-le pour éviter de te tromper de branche ou de worktree._")

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
