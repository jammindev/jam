"""The plugin's single door to the Orca CLI: where the binary is, how to call it.

The session start hook and the scripts all go through this module, so the
lookup order and the reading of the CLI's JSON live in one place.

Lookup order:
  1. JAM_ORCA_BIN, when set: an explicit choice. If it is not executable, the
     CLI is reported missing rather than silently replaced by another one.
  2. `orca` on the PATH.
  3. APP_BIN, where the Orca app installs its CLI on macOS.

Every call is `orca <args> --json`; the CLI answers {"id", "ok", "result"} and
only `result` is returned.
"""

import json
import os
import shutil
import subprocess

# Where the Orca app ships its CLI on macOS: the same on every Mac, so it is no
# machine-specific path. A module constant so the tests can replace it.
APP_BIN = "/Applications/Orca.app/Contents/Resources/bin/orca"

# Shown to agents and the maintainer: it names the three places, no path.
NOT_FOUND = ("CLI Orca introuvable : ni JAM_ORCA_BIN, ni orca dans le PATH, "
             "ni l'app Orca à son emplacement standard")


class OrcaError(Exception):
    """The CLI could not be run, or did not answer the way its contract says."""


def _executable(path):
    # isfile follows symlinks: a broken link (a known Orca install glitch)
    # counts as missing.
    return os.path.isfile(path) and os.access(path, os.X_OK)


def find_binary(environ=None):
    """Path of the Orca CLI, or None when there is none to run."""
    env = os.environ if environ is None else environ
    explicit = (env.get("JAM_ORCA_BIN") or "").strip()
    if explicit:
        return explicit if _executable(explicit) else None
    on_path = shutil.which("orca", path=env.get("PATH", os.defpath))
    if on_path:
        return on_path
    return APP_BIN if _executable(APP_BIN) else None


def call(*args, timeout=10, binary=None):
    """Run `orca <args> --json` and return its `result` object.

    Raises OrcaError when the CLI is missing, fails, is too slow, or prints
    anything other than {"ok": true, "result": {...}}.
    """
    binary = binary or find_binary()
    if binary is None:
        raise OrcaError(NOT_FOUND)
    label = "orca " + " ".join(args[:2])
    try:
        done = subprocess.run([binary, *args, "--json"], capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise OrcaError(f"{label} : pas de réponse en {timeout} s")
    except OSError as error:
        raise OrcaError(f"{label} : lancement impossible ({error.strerror})")
    if done.returncode != 0:
        reason = (done.stderr.strip().splitlines() or ["sans message"])[-1]
        raise OrcaError(f"{label} : échec (code {done.returncode}) : {reason}")
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise OrcaError(f"{label} : réponse JSON illisible")
    result = data.get("result") if isinstance(data, dict) else None
    if not isinstance(result, dict) or data.get("ok") is False:
        raise OrcaError(f"{label} : réponse inattendue")
    return result
