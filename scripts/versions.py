#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read versions.json, the single place that names the toolchain versions.

Usage:

    python3 scripts/versions.py KEY     # core, core_url, fqbn, STM32duinoBLE, STeaMi
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

VERSIONS_FILE = Path(__file__).resolve().parent.parent / "versions.json"


def load(path: Path = VERSIONS_FILE) -> dict:
    """Return the content of versions.json."""
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} KEY", file=sys.stderr)
        return 2
    data = load()
    if argv[1] not in data:
        print(
            f"error: unknown key {argv[1]!r} in versions.json (known: {', '.join(data)})",
            file=sys.stderr,
        )
        return 1
    print(data[argv[1]])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
