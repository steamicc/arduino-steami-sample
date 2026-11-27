# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for scripts/build-examples-archive.py (adapted from arduino-steami-lib)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build-examples-archive.py"
VERSIONS = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))

EXAMPLES = ("CAPTEURS/Distance", "BUZZER/Melodie")


def load_module():
    spec = importlib.util.spec_from_file_location("build_examples_archive", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, content: bytes = b"") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


class BuildExamplesArchiveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.repo = root / "repo"
        self.bins = root / "bins"
        self.out = root / "out.zip"
        for example in EXAMPLES:
            name = example.split("/")[1]
            write(self.repo / "examples" / example / f"{name}.ino", b"void setup() {}")
            write(self.bins / f"{example}.bin", f"bin-{example}".encode())

    def test_empty_repository_fails(self) -> None:
        empty = Path(self._tmp.name) / "empty"
        (empty / "examples").mkdir(parents=True)
        with self.assertRaises(SystemExit):
            self.mod.construire_index(empty, self.bins, "v1.0.0")

    def test_archive_is_reproducible(self) -> None:
        index = self.mod.construire_index(self.repo, self.bins, "v1.0.0")
        a = Path(self._tmp.name) / "a.zip"
        b = Path(self._tmp.name) / "b.zip"
        self.mod.ecrire_archive(index, self.bins, a)
        self.mod.ecrire_archive(index, self.bins, b)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_archive_is_reproducible_across_builds(self) -> None:
        """Two full builds from the same inputs give the same bytes."""
        a = Path(self._tmp.name) / "a.zip"
        b = Path(self._tmp.name) / "b.zip"
        for out in (a, b):
            index = self.mod.construire_index(self.repo, self.bins, "v1.0.0")
            self.mod.ecrire_archive(index, self.bins, out)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_core_version_is_configurable(self) -> None:
        index = self.mod.construire_index(self.repo, self.bins, "v1.0.0", "9.9.9")
        self.assertEqual(index["coeur"], "9.9.9")

    def test_core_and_fqbn_come_from_versions_json(self) -> None:
        index = self.mod.construire_index(self.repo, self.bins, "v1.0.0")
        self.assertEqual(index["coeur"], VERSIONS["core"])
        self.assertEqual(index["fqbn"], VERSIONS["fqbn"])

    def test_index_lists_every_example(self) -> None:
        index = self.mod.construire_index(self.repo, self.bins, "v1.0.0")
        self.assertEqual(index["version"], "v1.0.0")
        self.assertEqual(
            [e["id"] for e in index["exemples"]],
            ["BUZZER/Melodie", "CAPTEURS/Distance"],
        )
        entry = index["exemples"][1]
        data = (self.bins / "CAPTEURS/Distance.bin").read_bytes()
        self.assertEqual(entry["composant"], "CAPTEURS")
        self.assertEqual(entry["nom"], "Distance")
        self.assertEqual(entry["source"], "examples/CAPTEURS/Distance/Distance.ino")
        self.assertEqual(entry["bin"], "CAPTEURS/Distance.bin")
        self.assertEqual(entry["taille"], len(data))
        self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())

    def test_missing_bin_fails(self) -> None:
        (self.bins / "BUZZER/Melodie.bin").unlink()
        with self.assertRaises(SystemExit) as ctx:
            self.mod.construire_index(self.repo, self.bins, "v1.0.0")
        self.assertIn("BUZZER/Melodie", str(ctx.exception))

    def test_archive_layout(self) -> None:
        index = self.mod.construire_index(self.repo, self.bins, "v1.0.0")
        self.mod.ecrire_archive(index, self.bins, self.out)
        with zipfile.ZipFile(self.out) as zf:
            self.assertEqual(
                sorted(zf.namelist()),
                ["BUZZER/Melodie.bin", "CAPTEURS/Distance.bin", "index.json"],
            )
            self.assertEqual(json.loads(zf.read("index.json")), index)

    def test_stray_bin_is_not_archived(self) -> None:
        write(self.bins / "CAPTEURS/Inconnu.bin", b"stray")
        index = self.mod.construire_index(self.repo, self.bins, "v1.0.0")
        self.mod.ecrire_archive(index, self.bins, self.out)
        with zipfile.ZipFile(self.out) as zf:
            self.assertNotIn("CAPTEURS/Inconnu.bin", zf.namelist())

    def test_rejects_bad_tag(self) -> None:
        for tag in ("1.0.0", "v1.0", "v1.0.0-rc1"):
            with self.assertRaises(SystemExit, msg=tag):
                self.mod.construire_index(self.repo, self.bins, tag)


if __name__ == "__main__":
    unittest.main()
