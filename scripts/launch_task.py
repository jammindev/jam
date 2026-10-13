#!/usr/bin/env python3
"""Start a role in a task's worktree through the Orca CLI, under a cap.

    python3 scripts/launch_task.py --repo <repoId> --worktree <name>
        --role <role> --command <claude command> --brief <file>
        --cap <n> [--project-cap <m>] [--title <t>]

Steps, each stopping the launch when it fails:
  1. Count the running agents (`orca terminal list`): terminals with a
     non-empty agentIdentity whose `connected` is not false. Refused when the
     total reaches --cap, or when those of the project (worktreeId starting
     with "<repoId>::") reach --project-cap, before any other call. A
     truncated list cannot be counted: refused too.
  2. Find the worktree (`orca worktree ps`: same repoId, displayName = name),
     or create it (`orca worktree create ... --no-parent`).
  3. Open a terminal there running "JAM_ROLE=<role> <command>".
  4. Wait until the agent is ready (`tui-idle`), then send the brief, read
     from the file and sent as is. A brief typed before the agent is ready is
     lost, so it is not sent when the wait times out.

Exit codes:
  0 -> role started
  1 -> refused (a cap is reached, or a list is truncated)
  2 -> bad arguments, unreadable brief, or the Orca CLI failed
"""
import argparse
import re
import sys

import orca_cli

WAIT_MS = 60000  # how long Orca waits for the agent to be ready


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, f"[jam] {self.prog} : {message}\n")


class Refused(Exception):
    """The launch is refused on purpose (cap, truncated list)."""


def role_name(value):
    # The role ends up in a shell command line: only plain names get there.
    if not re.fullmatch(r"[a-z-]+", value):
        raise argparse.ArgumentTypeError(f"rôle invalide « {value} » (lettres a-z et tirets)")
    return value


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"plafond invalide « {value} » (au moins 1)")
    return number


def check_caps(repo, cap, project_cap):
    result = orca_cli.call("terminal", "list")
    rows = result.get("terminals")
    if not isinstance(rows, list):
        raise orca_cli.OrcaError("orca terminal list : réponse inattendue")
    if result.get("truncated"):
        raise Refused("liste des terminaux tronquée : agents impossibles à compter")
    agents = [row for row in rows if isinstance(row, dict)
              and isinstance(row.get("agentIdentity"), str) and row["agentIdentity"].strip()
              and row.get("connected") is not False]
    if len(agents) >= cap:
        raise Refused(f"plafond atteint : {len(agents)} agent(s) en cours pour {cap} au plus")
    if project_cap is not None:
        mine = [row for row in agents
                if str(row.get("worktreeId") or "").startswith(repo + "::")]
        if len(mine) >= project_cap:
            raise Refused(f"plafond du projet atteint : {len(mine)} agent(s) en cours "
                          f"pour {project_cap} au plus")


def find_or_create_worktree(repo, name):
    result = orca_cli.call("worktree", "ps")
    rows = result.get("worktrees")
    if not isinstance(rows, list):
        raise orca_cli.OrcaError("orca worktree ps : réponse inattendue")
    for row in rows:
        if (isinstance(row, dict) and row.get("repoId") == repo
                and row.get("displayName") == name and row.get("worktreeId")):
            return row["worktreeId"]
    if result.get("truncated"):
        # The worktree may exist beyond the list: creating it would make a twin.
        raise Refused(f"liste des worktrees tronquée : « {name} » introuvable, "
                      "création refusée")
    created = orca_cli.call("worktree", "create", "--repo", f"id:{repo}",
                            "--name", name, "--no-parent")
    worktree_id = (created.get("worktree") or {}).get("id")
    if not isinstance(worktree_id, str) or not worktree_id:
        raise orca_cli.OrcaError("orca worktree create : id du worktree absent")
    return worktree_id


def start_role(worktree_id, title, role, command, brief):
    created = orca_cli.call("terminal", "create", "--worktree", f"id:{worktree_id}",
                            "--title", title, "--command", f"JAM_ROLE={role} {command}")
    handle = (created.get("terminal") or {}).get("handle")
    if not isinstance(handle, str) or not handle:
        raise orca_cli.OrcaError("orca terminal create : handle du terminal absent")
    waited = orca_cli.call("terminal", "wait", "--terminal", handle, "--for", "tui-idle",
                           "--timeout-ms", str(WAIT_MS), timeout=WAIT_MS / 1000 + 30)
    if (waited.get("wait") or {}).get("satisfied") is not True:
        raise orca_cli.OrcaError(f"agent du terminal {handle} pas prêt après "
                                 f"{WAIT_MS // 1000} s : brief non envoyé")
    sent = orca_cli.call("terminal", "send", "--terminal", handle, "--text", brief, "--enter")
    if (sent.get("send") or {}).get("accepted") is not True:
        raise orca_cli.OrcaError(f"brief refusé par le terminal {handle}")
    return handle


def main():
    parser = Parser(prog="launch_task.py",
                    description="[jam] Lance un rôle dans le worktree d'une tâche, sous plafond.")
    parser.add_argument("--repo", required=True, help="id du repo Orca")
    parser.add_argument("--worktree", required=True, help="nom du worktree de la tâche")
    parser.add_argument("--role", required=True, type=role_name, help="rôle (JAM_ROLE)")
    parser.add_argument("--command", required=True, help="commande claude du rôle")
    parser.add_argument("--brief", required=True, help="fichier du brief")
    parser.add_argument("--cap", required=True, type=positive,
                        help="agents en cours au plus, tous projets")
    parser.add_argument("--project-cap", type=positive, help="agents en cours au plus, ce projet")
    parser.add_argument("--title", help="titre du terminal (le rôle par défaut)")
    args = parser.parse_args()

    try:
        with open(args.brief, encoding="utf-8") as fh:
            brief = fh.read()
    except OSError as error:
        print(f"[jam] brief illisible : {error.strerror} ({args.brief})", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print(f"[jam] brief illisible : pas en UTF-8 ({args.brief})", file=sys.stderr)
        sys.exit(2)

    try:
        check_caps(args.repo, args.cap, args.project_cap)
        worktree_id = find_or_create_worktree(args.repo, args.worktree)
        handle = start_role(worktree_id, args.title or args.role, args.role,
                            args.command, brief)
    except Refused as reason:
        print(f"[jam] lancement refusé : {reason}", file=sys.stderr)
        sys.exit(1)
    except orca_cli.OrcaError as error:
        print(f"[jam] lancement interrompu : {error}", file=sys.stderr)
        sys.exit(2)

    print(f"[jam] rôle {args.role} lancé dans le worktree « {args.worktree} » "
          f"(terminal {handle})")
    sys.exit(0)


if __name__ == "__main__":
    main()
