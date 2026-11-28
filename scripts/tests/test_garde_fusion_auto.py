# SPDX-License-Identifier: GPL-3.0-or-later
"""The auto-merge guard must stay the shared copy, byte for byte.

.github/scripts/garde-fusion-auto.sh is copied from the common source of the
steamicc robots (the same file in every repository that has a robot). It is
never edited here: change the common source, copy it again everywhere and
update REFERENCE below.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / ".github" / "scripts" / "garde-fusion-auto.sh"
REFERENCE = "661489204d121fe3a25dbeb533fab7123f77001dda9f138bc6a157506b983324"


def test_guard_matches_the_shared_copy() -> None:
    assert hashlib.sha256(GUARD.read_bytes()).hexdigest() == REFERENCE


def test_guard_is_executable() -> None:
    assert os.access(GUARD, os.X_OK)
