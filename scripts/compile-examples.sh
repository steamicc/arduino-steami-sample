#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Compile every sketch of examples/ with arduino-cli, for the STeaMi board.
#
# Requires arduino-cli and python3 on the PATH. The STM32 core, STM32duinoBLE
# and the STeaMi library are installed at the versions of versions.json (the
# only place that names them) when they are missing.
#
# The binary of each sketch is copied to DIR/<GROUP>/<Name>.bin (input of
# scripts/build-examples-archive.py). Every sketch is compiled, or only the
# ones given with --only (repeatable); each one that does not compile, or that
# does not exist, is named as "FAIL GROUP/Name" with the end of its log, and
# the script then exits with a non-zero code.
#
# Usage:
#   scripts/compile-examples.sh DIR [--examples EXAMPLES_DIR] [--only GROUP/Name]...

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
examples_dir="$script_dir/../examples"

usage="Usage: $0 DIR [--examples EXAMPLES_DIR] [--only GROUP/Name]..."
if [ "$#" -lt 1 ]; then
    echo "$usage" >&2
    exit 2
fi
out_arg="$1"
shift
only=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        --examples)
            [ "$#" -ge 2 ] || { echo "$usage" >&2; exit 2; }
            examples_dir="$2"
            shift 2
            ;;
        --only)
            [ "$#" -ge 2 ] || { echo "$usage" >&2; exit 2; }
            only+=("$2")
            shift 2
            ;;
        *)
            echo "$usage" >&2
            exit 2
            ;;
    esac
done
if [ ! -d "$examples_dir" ]; then
    echo "error: $examples_dir is not a directory" >&2
    exit 2
fi
examples_dir="$(cd "$examples_dir" && pwd)"
mkdir -p "$out_arg"
out_dir="$(cd "$out_arg" && pwd)"

version() { python3 "$script_dir/versions.py" "$1"; }
fqbn="$(version fqbn)"
core="$(version core)"
core_url="$(version core_url)"

# Core and libraries at the pinned versions. The index is refreshed only when
# the core is missing, so a warm run needs no network.
if ! arduino-cli core list 2>/dev/null | grep -q "STMicroelectronics:stm32 *${core}"; then
    arduino-cli core update-index --additional-urls "$core_url"
fi
# An install that fails (version missing from a stale index) is retried once
# after refreshing the index.
install_core() { arduino-cli core install "STMicroelectronics:stm32@${core}" --additional-urls "$core_url"; }
if ! install_core; then
    arduino-cli core update-index --additional-urls "$core_url"
    install_core
fi
lib_install() {
    if ! arduino-cli lib install "$@"; then
        arduino-cli lib update-index
        arduino-cli lib install "$@"
    fi
}
# Both libraries come from the Arduino Library Manager: "STeaMi" is published
# there by steamicc/arduino-steami-lib (one entry per release tag). arduino-cli
# downloads the library index on the first lib install.
# STeaMi declares "depends=STM32duinoBLE" without a version: installed with
# its dependencies, it would replace the pinned STM32duinoBLE with the latest
# one. So STM32duinoBLE is installed first at its pinned version, and STeaMi
# with --no-deps.
lib_install "STM32duinoBLE@$(version STM32duinoBLE)"
lib_install "STeaMi@$(version STeaMi)" --no-deps

total=0
passed=0
failed=0
log="$(mktemp)"
build_dir="$(mktemp -d)"
trap 'rm -rf "$log" "$build_dir"' EXIT

# Compile one sketch (id = GROUP/Name) and keep its binary as
# $out_dir/GROUP/Name.bin.
compile_sketch() {
    local id="$1"
    local name="${id#*/}"
    rm -f "$out_dir/$id.bin" # never keep a binary from an earlier run
    if [[ ! "$id" =~ ^[A-Z0-9_-]+/[A-Za-z0-9_]+$ ]]; then
        echo "error: $id is not a valid id (GROUP/Name, GROUP in upper case, Name in letters, digits, _)" >"$log"
        return 1
    fi
    if [ ! -f "$examples_dir/$id/$name.ino" ]; then
        echo "error: $id has no $name.ino: the sketch file must have the name of its folder" >"$log"
        return 1
    fi
    rm -rf "${build_dir:?}"/*
    arduino-cli compile --fqbn "$fqbn" --output-dir "$build_dir" \
        "$examples_dir/$id" >"$log" 2>&1 || return 1
    mkdir -p "$out_dir/${id%/*}"
    cp "$build_dir/$name.ino.bin" "$out_dir/$id.bin" >>"$log" 2>&1
}

# Compile one sketch and report it.
run_sketch() {
    local id="$1"
    total=$((total + 1))
    if compile_sketch "$id"; then
        passed=$((passed + 1))
        echo "PASS $id"
    else
        failed=$((failed + 1))
        echo "FAIL $id"
        tail -n 15 "$log" | sed 's/^/    /'
    fi
}

if [ "${#only[@]}" -gt 0 ]; then
    for id in "${only[@]}"; do
        run_sketch "$id"
    done
else
    while IFS= read -r folder; do
        [ -n "$folder" ] || continue
        run_sketch "${folder#"$examples_dir"/}"
    done < <(find "$examples_dir" -mindepth 2 -maxdepth 2 -type d | sort)
fi

echo "Total: $total | Passed: $passed | Failed: $failed"
if [ "$total" -eq 0 ]; then
    echo "error: no sketch found in $examples_dir" >&2
    exit 1
fi
[ "$failed" -eq 0 ]
