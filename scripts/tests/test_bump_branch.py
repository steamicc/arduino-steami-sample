# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for scripts/bump-branch.sh, with a local bare repository as origin."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "bump-branch.sh"
BOT = "robot[bot]"
BRANCH = "fix/steami-1.4.0"
TITLE = "fix(deps): Compile the sketches with STeaMi 1.4.0."


def git(cwd: Path, *args: str, author: str = "Someone") -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": author,
        "GIT_AUTHOR_EMAIL": "a@example.org",
        "GIT_COMMITTER_NAME": author,
        "GIT_COMMITTER_EMAIL": "a@example.org",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    result = subprocess.run(
        ["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def versions_text(steami: str) -> str:
    data = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    data["STeaMi"] = steami
    return json.dumps(data, indent=2) + "\n"


def commit_versions(repo: Path, steami: str, message: str, author: str = "Someone") -> str:
    (repo / "versions.json").write_text(versions_text(steami), encoding="utf-8")
    git(repo, "add", "versions.json")
    git(repo, "commit", "-q", "-m", message, author=author)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repos(tmp_path: Path) -> dict[str, Path]:
    """origin (bare), seed (pushes to origin) and work (the checkout of the run).

    work is cloned while main pins 1.2.3; main then moves on to 1.3.0 (an
    earlier bump of the robot that merged while the run waited).
    """
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    work = tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    git(tmp_path, "clone", "-q", str(origin), str(seed))
    commit_versions(seed, "1.2.3", "initial")
    git(seed, "push", "-q", "origin", "HEAD:main")
    git(tmp_path, "clone", "-q", str(origin), str(work))
    commit_versions(seed, "1.3.0", "fix(deps): STeaMi 1.3.0.", author=BOT)
    git(seed, "push", "-q", "origin", "HEAD:main")
    return {"origin": origin, "seed": seed, "work": work, "tmp": tmp_path}


def search_file(tmp: Path, available: list[str]) -> Path:
    path = tmp / "search.json"
    path.write_text(
        json.dumps({"libraries": [{"name": "STeaMi", "available_versions": available}]}),
        encoding="utf-8",
    )
    return path


def run(repos: dict[str, Path], tag: str = "v1.4.0") -> subprocess.CompletedProcess:
    env = {
        **os.environ,
        "TAG": tag,
        "SEARCH": str(search_file(repos["tmp"], ["1.2.3", "1.3.0", "1.4.0"])),
        "BRANCH": BRANCH,
        "TITLE": TITLE,
        "BOT": BOT,
        "PUSH_URL": str(repos["origin"]),
        "GIT_AUTHOR_NAME": BOT,
        "GIT_AUTHOR_EMAIL": "bot@example.org",
        "GIT_COMMITTER_NAME": BOT,
        "GIT_COMMITTER_EMAIL": "bot@example.org",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    return subprocess.run(
        ["bash", str(SCRIPT)], cwd=repos["work"], env=env, capture_output=True, text=True
    )


def remote_sha(repos: dict[str, Path], ref: str) -> str:
    return git(repos["origin"], "rev-parse", ref)


def remote_versions(repos: dict[str, Path], ref: str) -> dict:
    return json.loads(git(repos["origin"], "show", f"{ref}:versions.json"))


def test_branch_is_built_on_the_fresh_main(repos: dict[str, Path]) -> None:
    result = run(repos)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "result=pushed"
    main = remote_sha(repos, "main")
    assert remote_sha(repos, f"{BRANCH}^") == main
    assert git(repos["origin"], "log", "--format=%an %s", f"main..{BRANCH}") == f"{BOT} {TITLE}"
    expected = json.loads(versions_text("1.4.0"))
    assert remote_versions(repos, BRANCH) == expected


def test_fresh_main_that_already_pins_the_release_pushes_nothing(
    repos: dict[str, Path],
) -> None:
    commit_versions(repos["seed"], "1.4.0", "fix(deps): STeaMi 1.4.0 by hand.")
    git(repos["seed"], "push", "-q", "origin", "HEAD:main")
    result = run(repos)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "result=up-to-date"
    with pytest.raises(subprocess.CalledProcessError):
        remote_sha(repos, BRANCH)


def test_conflicting_branch_of_the_robot_is_rebuilt_from_main(
    repos: dict[str, Path],
) -> None:
    # The pull request the robot opened from the stale main (1.2.3 -> 1.4.0):
    # it conflicts with main (1.2.3 -> 1.3.0) on the "STeaMi" line.
    stale = repos["tmp"] / "stale"
    git(repos["tmp"], "clone", "-q", str(repos["origin"]), str(stale))
    git(stale, "reset", "-q", "--hard", "HEAD^")
    commit_versions(stale, "1.4.0", TITLE, author=BOT)
    git(stale, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    old = remote_sha(repos, BRANCH)

    result = run(repos)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "result=pushed"
    assert remote_sha(repos, BRANCH) != old
    assert remote_sha(repos, f"{BRANCH}^") == remote_sha(repos, "main")
    assert remote_versions(repos, BRANCH)["STeaMi"] == "1.4.0"


def test_branch_with_a_commit_of_somebody_else_is_left_alone(
    repos: dict[str, Path],
) -> None:
    git(repos["seed"], "switch", "-q", "-c", BRANCH)
    commit_versions(repos["seed"], "1.4.0", "prepared by hand", author="Maintainer")
    git(repos["seed"], "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    before = remote_sha(repos, BRANCH)

    result = run(repos)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "result=foreign"
    assert remote_sha(repos, BRANCH) == before


def test_foreign_commits_win_over_an_up_to_date_main(repos: dict[str, Path]) -> None:
    """The caller deletes the branch on up-to-date: never one with foreign work."""
    git(repos["seed"], "switch", "-q", "-c", BRANCH)
    commit_versions(repos["seed"], "1.4.0", "prepared by hand", author="Maintainer")
    git(repos["seed"], "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    git(repos["seed"], "switch", "-q", "main")
    commit_versions(repos["seed"], "1.4.0", "fix(deps): STeaMi 1.4.0 by hand.")
    git(repos["seed"], "push", "-q", "origin", "HEAD:main")

    result = run(repos)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "result=foreign"


def test_unreachable_origin_fails(repos: dict[str, Path]) -> None:
    git(repos["work"], "remote", "set-url", "origin", str(repos["tmp"] / "missing.git"))
    result = run(repos)
    assert result.returncode != 0
    assert "result=" not in result.stdout


def test_stale_remote_tracking_ref_of_the_checkout_is_ignored(
    repos: dict[str, Path],
) -> None:
    """A branch deleted during the wait is created again, with no lease on its old sha."""
    git(repos["seed"], "switch", "-q", "-c", BRANCH)
    commit_versions(repos["seed"], "1.4.0", TITLE, author=BOT)
    git(repos["seed"], "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    git(repos["work"], "fetch", "-q", "origin")
    git(repos["seed"], "push", "-q", "origin", f":refs/heads/{BRANCH}")

    result = run(repos)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "result=pushed"
    assert remote_sha(repos, f"{BRANCH}^") == remote_sha(repos, "main")


def test_push_is_refused_when_the_branch_moved_since_the_check(
    repos: dict[str, Path],
) -> None:
    # PUSH_URL is the same repository as origin in the workflow; a copy whose
    # branch differs stands for a push made between the check and the push.
    moved = repos["tmp"] / "moved.git"
    git(repos["tmp"], "clone", "-q", "--bare", str(repos["origin"]), str(moved))
    git(repos["seed"], "switch", "-q", "-c", BRANCH)
    commit_versions(repos["seed"], "1.4.0", "pushed meanwhile", author="Maintainer")
    git(repos["seed"], "push", "-q", str(moved), f"HEAD:refs/heads/{BRANCH}")
    before = git(moved, "rev-parse", BRANCH)

    env_url = repos["origin"]
    repos["origin"] = moved  # what run() passes as PUSH_URL
    git(repos["work"], "remote", "set-url", "origin", str(env_url))
    result = run(repos)
    assert result.returncode != 0
    assert "result=pushed" not in result.stdout
    assert git(moved, "rev-parse", BRANCH) == before
