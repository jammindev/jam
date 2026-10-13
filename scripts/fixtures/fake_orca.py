"""Fake Orca CLI for the tests of the plugin's scripts.

The tests never talk to a real Orca. FakeOrca writes, in a temp folder, an
executable `orca` that runs main() below. main() answers each call with the
next response queued for its command ("worktree ps", "terminal list"...): the
last one repeats once the queue is used up, an unknown command exits 2. Every
call is logged, so a test can assert the exact arguments the script passed.

The responses usually start from the files in fixtures/orca/: example outputs
of the real CLI, cut down to the fields the scripts read. They are the
contract the tests check (the full reference stays `orca skills get orca-cli`).
"""

import copy
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "orca")


def fixture(name):
    """A fresh copy of fixtures/orca/<name>.json, free to modify."""
    with open(os.path.join(FIXTURES, name + ".json"), encoding="utf-8") as fh:
        return copy.deepcopy(json.load(fh))


def reply(document, sleep=0):
    """The CLI prints this JSON document and exits 0."""
    return {"stdout": json.dumps(document), "sleep": sleep}


def failure(code=1, stderr="orca: app not running"):
    return {"exit": code, "stderr": stderr}


def garbage():
    return {"stdout": "{ this is not json"}


class FakeOrca:

    def __init__(self, folder):
        os.makedirs(folder, exist_ok=True)
        self.folder = folder
        self.binary = os.path.join(folder, "orca")
        self.responses = {}
        with open(self.binary, "w") as fh:
            fh.write("#!%s\nimport sys\nsys.path.insert(0, %r)\n"
                     "import fake_orca\nfake_orca.main()\n" % (sys.executable, HERE))
        os.chmod(self.binary, 0o755)
        self._save()

    def respond(self, command, *responses):
        """Queue the responses to `orca <command> ...`, in order."""
        self.responses[command] = list(responses)
        self._save()

    def calls(self):
        """The argument lists of every call so far, in order."""
        try:
            with open(os.path.join(self.folder, "calls.log"), encoding="utf-8") as fh:
                return [json.loads(line) for line in fh]
        except FileNotFoundError:
            return []

    def _save(self):
        with open(os.path.join(self.folder, "spec.json"), "w", encoding="utf-8") as fh:
            json.dump(self.responses, fh)


def main():
    folder = os.path.dirname(os.path.abspath(sys.argv[0]))
    args = sys.argv[1:]
    with open(os.path.join(folder, "calls.log"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(args) + "\n")
    with open(os.path.join(folder, "spec.json"), encoding="utf-8") as fh:
        responses = json.load(fh)

    command = " ".join(args[:2])
    queue = responses.get(command)
    if not queue:
        sys.stderr.write("unexpected call: %r\n" % (args,))
        sys.exit(2)

    # One counter per command: the n-th call gets the n-th response.
    counts_path = os.path.join(folder, "counts.json")
    try:
        with open(counts_path, encoding="utf-8") as fh:
            counts = json.load(fh)
    except FileNotFoundError:
        counts = {}
    index = counts.get(command, 0)
    counts[command] = index + 1
    with open(counts_path, "w", encoding="utf-8") as fh:
        json.dump(counts, fh)

    response = queue[min(index, len(queue) - 1)]
    time.sleep(response.get("sleep", 0))
    if "stdout" in response:
        sys.stdout.write(response["stdout"] + "\n")
    if "stderr" in response:
        sys.stderr.write(response["stderr"] + "\n")
    sys.exit(response.get("exit", 0))
