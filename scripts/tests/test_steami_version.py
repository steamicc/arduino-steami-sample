# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for scripts/steami-version.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "steami-version.py"
PINNED = "1.2.3"


@pytest.fixture
def versions(tmp_path: Path) -> Path:
    data = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    text = json.dumps(data, indent=2) + "\n"
    text = text.replace(f'"STeaMi": "{data["STeaMi"]}"', f'"STeaMi": "{PINNED}"')
    path = tmp_path / "versions.json"
    path.write_text(text, encoding="utf-8")
    return path


def search(tmp_path: Path, available: list[str]) -> str:
    path = tmp_path / "search.json"
    path.write_text(
        json.dumps(
            {
                "libraries": [
                    {"name": "STeaMi", "available_versions": available},
                    {"name": "STeaMi-Extra", "available_versions": ["9.9.9"]},
                ],
                "status": "success",
            }
        ),
        encoding="utf-8",
    )
    return str(path)


def run_raw(versions: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--versions", str(versions), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def run(versions: Path, *args: str) -> str:
    result = run_raw(versions, *args)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_published_equal_or_older_is_up_to_date(versions: Path) -> None:
    assert run(versions, "--released", "v1.2.3") == "state=up-to-date\nversion=1.2.3\n"
    assert run(versions, "--released", "v1.2.2") == "state=up-to-date\nversion=1.2.2\n"


def test_newer_without_search_is_new(versions: Path) -> None:
    assert run(versions, "--released", "v1.3.0") == "state=new\nversion=1.3.0\n"


def test_newer_unknown_to_the_library_manager_waits(versions: Path, tmp_path: Path) -> None:
    out = run(versions, "--released", "v1.3.0", "--search", search(tmp_path, ["1.2.3"]))
    assert out == "state=wait\nversion=1.3.0\n"


def test_other_libraries_are_ignored(versions: Path, tmp_path: Path) -> None:
    out = run(versions, "--released", "v9.9.9", "--search", search(tmp_path, ["1.2.3"]))
    assert out == "state=wait\nversion=9.9.9\n"


def test_numeric_comparison_and_bump(versions: Path, tmp_path: Path) -> None:
    out = run(
        versions, "--released", "v1.10.0", "--search", search(tmp_path, ["1.2.3", "1.10.0"])
    )
    assert out == "state=bump\nversion=1.10.0\n"


def test_write_changes_only_the_steami_value(versions: Path, tmp_path: Path) -> None:
    before = versions.read_text(encoding="utf-8")
    run(
        versions,
        "--released", "v1.10.0",
        "--search", search(tmp_path, ["1.2.3", "1.10.0"]),
        "--write",
    )
    after = versions.read_text(encoding="utf-8")
    assert after == before.replace('"STeaMi": "1.2.3"', '"STeaMi": "1.10.0"')


@pytest.mark.parametrize("released", ["v1.3.0", "v1.2.3"])
def test_write_does_nothing_unless_bump(versions: Path, tmp_path: Path, released: str) -> None:
    before = versions.read_bytes()
    run(versions, "--released", released, "--search", search(tmp_path, ["1.2.3"]), "--write")
    assert versions.read_bytes() == before


def test_bad_tag_is_refused(versions: Path) -> None:
    result = run_raw(versions, "--released", "1.3")
    assert result.returncode == 2
    assert "1.3" in result.stderr
