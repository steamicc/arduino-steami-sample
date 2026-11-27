# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for scripts/compile-examples.sh, with a fake arduino-cli on the PATH."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "compile-examples.sh"
VERSIONS = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))

# Records its arguments, writes <sketch>.ino.bin in --output-dir, fails when
# the sketch folder holds a file named FAIL.
FAKE_ARDUINO_CLI = """#!/usr/bin/env bash
echo "$*" >> "$FAKE_LOG"
case "$1" in
  core)
    if [ "$2" = "list" ]; then exit 0; fi
    exit 0 ;;
  lib) exit 0 ;;
  compile)
    out=""; sketch=""
    args=("$@")
    for ((i = 1; i < ${#args[@]}; i++)); do
      if [ "${args[$i]}" = "--output-dir" ]; then out="${args[$((i + 1))]}"; fi
    done
    sketch="${args[$((${#args[@]} - 1))]}"
    if [ -e "$sketch/FAIL" ]; then
      echo "$sketch/$(basename "$sketch").ino:3:1: error: broken" >&2
      exit 1
    fi
    mkdir -p "$out"
    echo "bin of $(basename "$sketch")" > "$out/$(basename "$sketch").ino.bin"
    exit 0 ;;
esac
exit 0
"""


@pytest.fixture
def env(tmp_path: Path):
    fakebin = tmp_path / "fakebin"
    fakebin.mkdir()
    cli = fakebin / "arduino-cli"
    cli.write_text(FAKE_ARDUINO_CLI, encoding="utf-8")
    cli.chmod(0o755)
    log = tmp_path / "cli.log"
    environment = dict(os.environ)
    environment["PATH"] = f"{fakebin}:{environment['PATH']}"
    environment["FAKE_LOG"] = str(log)
    return environment, log, tmp_path


def sketch(examples: Path, group: str, name: str, ino: str | None = None) -> Path:
    folder = examples / group / name
    folder.mkdir(parents=True)
    (folder / f"{ino or name}.ino").write_text("void setup() {}\nvoid loop() {}\n")
    return folder


def run(env, examples: Path, out: Path) -> subprocess.CompletedProcess:
    environment, _, _ = env
    return subprocess.run(
        ["bash", str(SCRIPT), str(out), "--examples", str(examples)],
        capture_output=True,
        text=True,
        env=environment,
    )


def test_one_sketch_gives_one_bin(env) -> None:
    _, _, tmp = env
    examples = tmp / "examples"
    sketch(examples, "BOUTONS", "LedsBoutons")
    result = run(env, examples, tmp / "out")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp / "out" / "BOUTONS" / "LedsBoutons.bin").read_text() == "bin of LedsBoutons\n"
    assert "PASS BOUTONS/LedsBoutons" in result.stdout


def test_every_sketch_is_compiled(env) -> None:
    _, _, tmp = env
    examples = tmp / "examples"
    sketch(examples, "BOUTONS", "LedsBoutons")
    sketch(examples, "BUZZER", "Melodie")
    result = run(env, examples, tmp / "out")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp / "out" / "BUZZER" / "Melodie.bin").is_file()
    assert "Total: 2 | Passed: 2 | Failed: 0" in result.stdout


def test_versions_come_from_versions_json(env) -> None:
    _, log, tmp = env
    examples = tmp / "examples"
    sketch(examples, "BOUTONS", "LedsBoutons")
    assert run(env, examples, tmp / "out").returncode == 0
    calls = log.read_text()
    assert f"STMicroelectronics:stm32@{VERSIONS['core']}" in calls
    assert f"STM32duinoBLE@{VERSIONS['STM32duinoBLE']}" in calls
    assert f"STeaMi@{VERSIONS['STeaMi']}" in calls
    assert VERSIONS["core_url"] in calls
    assert f"--fqbn {VERSIONS['fqbn']}" in calls


def test_steami_does_not_replace_the_pinned_ble_library(env) -> None:
    """STeaMi depends on STM32duinoBLE without a version: installing it with
    its dependencies replaces the pinned STM32duinoBLE with the latest one."""
    _, log, tmp = env
    examples = tmp / "examples"
    sketch(examples, "BOUTONS", "LedsBoutons")
    assert run(env, examples, tmp / "out").returncode == 0
    installs = [line for line in log.read_text().splitlines() if line.startswith("lib install")]
    assert installs == [
        f"lib install STM32duinoBLE@{VERSIONS['STM32duinoBLE']}",
        f"lib install STeaMi@{VERSIONS['STeaMi']} --no-deps",
    ]


def test_misnamed_ino_fails_and_names_the_folder(env) -> None:
    _, _, tmp = env
    examples = tmp / "examples"
    sketch(examples, "BOUTONS", "LedsBoutons", ino="Autre")
    result = run(env, examples, tmp / "out")
    assert result.returncode != 0
    assert "BOUTONS/LedsBoutons" in result.stdout + result.stderr
    assert not (tmp / "out" / "BOUTONS" / "LedsBoutons.bin").exists()


def test_invalid_id_fails(env) -> None:
    _, _, tmp = env
    examples = tmp / "examples"
    sketch(examples, "boutons", "Leds-Boutons")
    result = run(env, examples, tmp / "out")
    assert result.returncode != 0
    assert "boutons/Leds-Boutons" in result.stdout + result.stderr


def test_compilation_error_fails_and_names_the_sketch(env) -> None:
    _, _, tmp = env
    examples = tmp / "examples"
    sketch(examples, "BOUTONS", "LedsBoutons")
    broken = sketch(examples, "BUZZER", "Melodie")
    (broken / "FAIL").write_text("")
    result = run(env, examples, tmp / "out")
    assert result.returncode != 0
    assert "FAIL BUZZER/Melodie" in result.stdout
    assert "broken" in result.stdout
    assert "Failed: 1" in result.stdout


def test_stale_bin_is_not_kept_when_compilation_fails(env) -> None:
    _, _, tmp = env
    examples = tmp / "examples"
    broken = sketch(examples, "BUZZER", "Melodie")
    (broken / "FAIL").write_text("")
    stale = tmp / "out" / "BUZZER" / "Melodie.bin"
    stale.parent.mkdir(parents=True)
    stale.write_text("old")
    assert run(env, examples, tmp / "out").returncode != 0
    assert not stale.exists()


def test_no_sketch_is_an_error(env) -> None:
    _, _, tmp = env
    (tmp / "examples").mkdir()
    result = run(env, tmp / "examples", tmp / "out")
    assert result.returncode != 0
    assert "no sketch" in result.stdout + result.stderr
