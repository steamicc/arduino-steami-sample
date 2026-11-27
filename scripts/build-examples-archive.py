#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bundle the compiled sketches into a zip with an index.json.

The .bin files come from `scripts/compile-examples.sh BIN_DIR` (layout
BIN_DIR/<GROUP>/<Name>.bin). The archive holds index.json and the .bin files
at the paths listed in the index. The format is the one of the examples
archive of arduino-steami-lib, which the STeaMi wiki reads. The core version
and the board (FQBN) come from versions.json.

Usage:

    python3 scripts/build-examples-archive.py --bins build/bins \
        --tag v1.0.0 --out steami-exemples-v1.0.0.zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import versions  # noqa: E402

TAG = re.compile(r"^v\d+\.\d+\.\d+$")


def construire_index(
    repo_dir: Path,
    bins_dir: Path,
    tag: str,
    coeur: str | None = None,
    fqbn: str | None = None,
) -> dict:
    """Build the index of every sketch, checking each .bin exists."""
    if not TAG.match(tag):
        raise SystemExit(f"error: tag {tag!r} must look like vX.Y.Z")
    pins = versions.load()
    coeur = coeur or pins["core"]
    fqbn = fqbn or pins["fqbn"]

    exemples = []
    for ino in sorted((repo_dir / "examples").glob("*/*/*.ino")):
        nom = ino.parent.name
        composant = ino.parent.parent.name
        if ino.stem != nom:
            continue
        id_ = f"{composant}/{nom}"
        bin_rel = f"{composant}/{nom}.bin"
        bin_path = bins_dir / bin_rel
        if not bin_path.is_file():
            raise SystemExit(f"error: missing .bin for example {id_} ({bin_path})")
        data = bin_path.read_bytes()
        exemples.append(
            {
                "id": id_,
                "composant": composant,
                "nom": nom,
                "bin": bin_rel,
                "taille": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "source": f"examples/{composant}/{nom}/{nom}.ino",
            }
        )
    if not exemples:
        raise SystemExit(f"error: no example found in {repo_dir / 'examples'}")
    exemples.sort(key=lambda e: e["id"])

    return {
        "version": tag,
        "fqbn": fqbn,
        "coeur": coeur,
        "exemples": exemples,
    }


def ecrire_archive(index: dict, bins_dir: Path, sortie: Path) -> None:
    """Write index.json and the listed .bin files into a zip."""
    sortie.parent.mkdir(parents=True, exist_ok=True)

    # Fixed timestamps and permissions, sorted entries: the same inputs give
    # the same bytes.
    def ajouter(zf: zipfile.ZipFile, nom: str, data: bytes) -> None:
        info = zipfile.ZipInfo(nom, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        zf.writestr(info, data)

    with zipfile.ZipFile(sortie, "w") as zf:
        index_json = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
        ajouter(zf, "index.json", index_json.encode("utf-8"))
        for exemple in sorted(index["exemples"], key=lambda e: e["bin"]):
            ajouter(zf, exemple["bin"], (bins_dir / exemple["bin"]).read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root holding examples/ (default: this repository)",
    )
    parser.add_argument("--bins", required=True, type=Path, help="compiled .bin directory")
    parser.add_argument("--tag", required=True, help="release tag, vX.Y.Z")
    parser.add_argument("--out", required=True, type=Path, help="output zip file")
    args = parser.parse_args()

    index = construire_index(args.repo, args.bins, args.tag)
    ecrire_archive(index, args.bins, args.out)
    print(f"{args.out}: {len(index['exemples'])} examples")


if __name__ == "__main__":
    main()
