# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for versions.json and scripts/versions.py."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "versions.py"
KEYS = {"core", "core_url", "fqbn", "STM32duinoBLE", "STeaMi"}


def load_module():
    spec = importlib.util.spec_from_file_location("versions", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_versions_json_is_valid() -> None:
    data = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    assert set(data) == KEYS
    assert all(isinstance(v, str) and v for v in data.values())
    for key in ("core", "STM32duinoBLE", "STeaMi"):
        assert re.fullmatch(r"\d+\.\d+\.\d+", data[key]), key
    assert data["fqbn"].count(":") == 2
    assert data["core_url"].startswith("https://")


def test_load_returns_the_file() -> None:
    mod = load_module()
    assert mod.load() == json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))


def test_cli_prints_one_value() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "core"], capture_output=True, text=True, check=True
    )
    data = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    assert result.stdout == data["core"] + "\n"


def test_cli_refuses_unknown_key() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "nope"], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "nope" in result.stderr


def test_no_version_is_written_elsewhere() -> None:
    """versions.json is the only place that names the toolchain versions."""
    data = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    files = [
        p
        for pattern in ("scripts/*.sh", "scripts/*.py", ".github/workflows/*.yml")
        for p in ROOT.glob(pattern)
    ]
    assert files, "no script or workflow found"
    for path in files:
        text = path.read_text(encoding="utf-8")
        for key, value in data.items():
            assert value not in text, f"{path.relative_to(ROOT)} repeats {key} ({value})"
