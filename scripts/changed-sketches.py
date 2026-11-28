#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the sketches a pull request can break.

Usage:

    python3 scripts/changed-sketches.py --base BASE_SHA --head HEAD_SHA

Run it at the root of a repository whose working tree is checked out at HEAD
(or at the merge commit of the pull request), with the history of BASE: it
lists the changed paths with `git diff --name-only --no-renames -z
BASE...HEAD` (a rename counts as a deletion plus an addition) and reads the
working tree to know which sketch folders still exist.

It prints one line of JSON on the standard output:

    {"all": false, "sketches": ["GROUP/Name", ...]}

"all" is true when the change may affect every sketch (shared file, unknown
file): the caller then compiles everything. Otherwise "sketches" lists, sorted
and without duplicates, the sketches to compile. When in doubt, all is true.
The script fails (non-zero exit code) if git fails: the caller must not
compile nothing in that case.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

# Files that change what every sketch is compiled with.
SHARED = {
    "versions.json",
    "scripts/compile-examples.sh",
    "scripts/versions.py",
    "scripts/changed-sketches.py",
    ".github/workflows/ci.yml",
}

# Files that cannot change the result of a sketch compilation (fnmatch
# patterns; "*" also matches "/"). Markdown files under examples/ are not
# listed: they are handled with the sketches.
SANS_EFFET = (
    "README*",
    "*.md",
    ".github/workflows/release.yml",
    ".github/workflows/examples-archive.yml",
    "scripts/build-examples-archive.py",
    "scripts/tests/*",
    "package*.json",
    ".releaserc*",
    ".github/ISSUE_TEMPLATE/*",
)


def select(changed: list[str], root: Path) -> dict:
    """Return {"all": bool, "sketches": [GROUP/Name, ...]} for the changed paths.

    root is the working tree checked out at the head of the change.
    """
    sketches: set[str] = set()
    for path in changed:
        if path in SHARED:
            return {"all": True, "sketches": []}
        parts = path.split("/")
        if parts[0] == "examples":
            if len(parts) < 4:
                return {"all": True, "sketches": []}
            # A folder that still exists is compiled by the release even
            # without its <Name>.ino: --only then fails in the pull request.
            if (root / "examples" / parts[1] / parts[2]).is_dir():
                sketches.add(f"{parts[1]}/{parts[2]}")
            continue
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in SANS_EFFET):
            continue
        return {"all": True, "sketches": []}
    return {"all": False, "sketches": sorted(sketches)}


def changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", "-z", f"{base}...{head}"],
        capture_output=True,
        check=True,
    )
    return [p.decode("utf-8") for p in result.stdout.split(b"\0") if p]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args(argv[1:])
    try:
        changed = changed_paths(args.base, args.head)
    except subprocess.CalledProcessError as error:
        print(error.stderr.decode("utf-8", "replace"), file=sys.stderr)
        return 1
    print(json.dumps(select(changed, Path.cwd())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
