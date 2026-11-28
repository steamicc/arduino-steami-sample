# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for scripts/changed-sketches.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "changed-sketches.py"


def load_module():
    spec = importlib.util.spec_from_file_location("changed_sketches", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


select = None


@pytest.fixture(autouse=True)
def _load() -> None:
    global select
    select = load_module().select


@pytest.fixture
def root(tmp_path: Path) -> Path:
    folder = tmp_path / "examples" / "PREMIERS" / "ClignoterLed"
    folder.mkdir(parents=True)
    (folder / "ClignoterLed.ino").write_text("void setup() {}\nvoid loop() {}\n")
    return tmp_path


def test_documentation_changes_nothing(root: Path) -> None:
    assert select(["README.md"], root) == {"all": False, "sketches": []}


def test_changed_sketch_is_selected(root: Path) -> None:
    assert select(["examples/PREMIERS/ClignoterLed/ClignoterLed.ino"], root) == {
        "all": False,
        "sketches": ["PREMIERS/ClignoterLed"],
    }


def test_sketches_are_sorted_without_duplicates(root: Path) -> None:
    other = root / "examples" / "BUZZER" / "Melodie"
    other.mkdir(parents=True)
    (other / "Melodie.ino").write_text("")
    changed = [
        "examples/PREMIERS/ClignoterLed/ClignoterLed.ino",
        "examples/BUZZER/Melodie/Melodie.ino",
        "examples/PREMIERS/ClignoterLed/notes.h",
    ]
    assert select(changed, root) == {
        "all": False,
        "sketches": ["BUZZER/Melodie", "PREMIERS/ClignoterLed"],
    }


def test_deleted_sketch_is_ignored(root: Path) -> None:
    assert select(["examples/BUZZER/Melodie/Melodie.ino"], root) == {
        "all": False,
        "sketches": [],
    }


def test_folder_without_its_ino_is_still_selected(root: Path) -> None:
    """The release compiles the folder: --only must fail in the PR."""
    folder = root / "examples" / "PREMIERS" / "X"
    folder.mkdir()
    (folder / "autre.h").write_text("")
    assert select(["examples/PREMIERS/X/X.ino"], root)["sketches"] == ["PREMIERS/X"]


def test_other_path_under_examples_compiles_all(root: Path) -> None:
    assert select(["examples/README.md"], root)["all"] is True


@pytest.mark.parametrize(
    "path",
    [
        "versions.json",
        "scripts/compile-examples.sh",
        "scripts/versions.py",
        "scripts/changed-sketches.py",
        ".github/workflows/ci.yml",
    ],
)
def test_shared_file_compiles_all(root: Path, path: str) -> None:
    assert select([path], root)["all"] is True


def test_files_without_effect_change_nothing(root: Path) -> None:
    changed = [
        ".github/workflows/release.yml",
        ".github/workflows/examples-archive.yml",
        "scripts/build-examples-archive.py",
        "scripts/steami-version.py",
        ".github/workflows/suivre-bibliotheque.yml",
        "scripts/tests/test_x.py",
        "package.json",
        "package-lock.json",
        ".releaserc.json",
        ".github/ISSUE_TEMPLATE/bug.md",
        "docs/x.md",
    ]
    assert select(changed, root) == {"all": False, "sketches": []}


def test_unknown_file_compiles_all(root: Path) -> None:
    assert select(["scripts/nouveau-helper.sh"], root)["all"] is True


def test_cli_on_a_git_repo(tmp_path: Path) -> None:
    def git(*args: str) -> str:
        return subprocess.run(
            [
                "git",
                "-c", "user.name=Test",
                "-c", "user.email=test@example.org",
                "-c", "commit.gpgsign=false",
                *args,
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    ino = tmp_path / "examples" / "PREMIERS" / "ClignoterLed" / "ClignoterLed.ino"
    ino.parent.mkdir(parents=True)
    ino.write_text("void setup() {}\nvoid loop() {}\n")
    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    first = git("rev-parse", "HEAD")
    ino.write_text("// changed\nvoid setup() {}\nvoid loop() {}\n")
    git("commit", "-q", "-a", "-m", "two")
    second = git("rev-parse", "HEAD")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--base", first, "--head", second],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == '{"all": false, "sketches": ["PREMIERS/ClignoterLed"]}'
