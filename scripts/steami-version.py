#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare the published STeaMi library with the version of versions.json.

Usage:

    python3 scripts/steami-version.py --released vX.Y.Z [--search FILE]
                                      [--write] [--versions PATH]

--released is the tag of the published release of the library. --search is the
output of `arduino-cli lib search STeaMi --format json`: it tells whether the
Arduino Library Manager already knows the version. It prints lines ready for
$GITHUB_OUTPUT:

    state=<up-to-date|new|wait|bump>
    version=X.Y.Z

up-to-date: the published version is not newer than the pinned one (never go
            back);
new:        newer, and no search result to say whether the Library Manager has it;
wait:       newer, but not in the available_versions of the "STeaMi" library;
bump:       newer and available. With --write, only the value of "STeaMi" is
            changed in versions.json (the rest of the file stays as it is).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY = "STeaMi"


def _load_versions_module():
    spec = importlib.util.spec_from_file_location("versions", HERE / "versions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def triplet(text: str) -> tuple[int, int, int]:
    """Return (major, minor, patch) of "X.Y.Z" or "vX.Y.Z"; ValueError otherwise."""
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text.strip())
    if not match:
        raise ValueError(f"not a version X.Y.Z: {text!r}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def available_versions(search: dict) -> list[str]:
    """Return the available_versions of the library named exactly "STeaMi"."""
    for library in search.get("libraries", []):
        if library.get("name") == KEY:
            return list(library.get("available_versions", []))
    return []


def decide(released: str, pinned: str, available: list[str] | None) -> str:
    if triplet(released) <= triplet(pinned):
        return "up-to-date"
    if available is None:
        return "new"
    known = set()
    for version in available:
        try:
            known.add(triplet(version))
        except ValueError:
            continue
    return "bump" if triplet(released) in known else "wait"


def write_version(path: Path, version: str) -> None:
    """Replace the value of "STeaMi", and nothing else, in versions.json."""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'("' + KEY + r'"\s*:\s*")[^"]*(")')
    new_text, count = pattern.subn(lambda m: m.group(1) + version + m.group(2), text)
    if count != 1:
        raise ValueError(f'"{KEY}" not found exactly once in {path}')
    path.write_text(new_text, encoding="utf-8")


def main(argv: list[str]) -> int:
    versions = _load_versions_module()
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--released", required=True, help="tag of the published release")
    parser.add_argument("--search", type=Path, help="arduino-cli lib search JSON output")
    parser.add_argument("--write", action="store_true", help="write the version on bump")
    parser.add_argument("--versions", type=Path, default=versions.VERSIONS_FILE)
    args = parser.parse_args(argv)

    try:
        triplet(args.released)
        pinned = versions.load(args.versions)[KEY]
        available = None
        if args.search is not None:
            available = available_versions(json.loads(args.search.read_text(encoding="utf-8")))
        state = decide(args.released, pinned, available)
        version = args.released.strip().removeprefix("v")
        if args.write and state == "bump":
            write_version(args.versions, version)
    except (ValueError, KeyError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"state={state}")
    print(f"version={version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
