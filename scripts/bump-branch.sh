#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the branch of a STeaMi bump from the current main of origin, and push
# it. Used by .github/workflows/suivre-bibliotheque.yml, to open the pull
# request and to rebuild it when it conflicts with main.
#
# main is fetched again here, not taken from the checkout of the run: the run
# waits for the Library Manager (up to 30 min), and an earlier bump of the
# robot can merge meanwhile. A branch made from the old main would conflict
# with it on the "STeaMi" line.
#
# Run it at the root of the repository, with a clean working tree and the
# identity of the commit already set. Environment:
#
#   TAG       tag of the published release (vX.Y.Z)
#   SEARCH    output of `arduino-cli lib search STeaMi --format json`
#   BRANCH    branch of the bump (fix/steami-X.Y.Z)
#   TITLE     message of the commit
#   BOT       author name of the robot's commits (<app-slug>[bot])
#   PUSH_URL  where to push (default: origin)
#
# The last line of the standard output is the result:
#
#   result=pushed      the branch is main plus one commit of the robot that
#                      pins the release;
#   result=up-to-date  main already pins the release or a newer one: nothing
#                      pushed;
#   result=foreign     the branch has commits that are not the robot's:
#                      nothing pushed (checked first, so that up-to-date
#                      always means a branch of the robot or no branch).
#
# Any other failure (git, network, a push refused by the lease) exits with a
# non-zero code and prints no result.

set -euo pipefail

for name in TAG SEARCH BRANCH TITLE BOT; do
    if [ -z "${!name:-}" ]; then
        echo "error: $name is not set" >&2
        exit 2
    fi
done
push_url="${PUSH_URL:-origin}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

git fetch --quiet origin "+refs/heads/main:refs/remotes/origin/main"

# The branch as it is now on origin (not a remote-tracking ref of the
# checkout, which can be older than the run).
set +e
git ls-remote --exit-code origin "refs/heads/$BRANCH" > /dev/null
status=$?
set -e
case "$status" in
    0)
        git fetch --quiet origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"
        remote_sha="$(git rev-parse --verify "refs/remotes/origin/$BRANCH")"
        ;;
    2)
        remote_sha=""
        ;;
    *)
        echo "error: git ls-remote failed for $BRANCH" >&2
        exit 1
        ;;
esac

# Never overwrite the work of somebody else on this branch name.
if [ -n "$remote_sha" ]; then
    foreign="$(git log --format='%an' "origin/main..$remote_sha" | grep -vxF "$BOT" || true)"
    if [ -n "$foreign" ]; then
        echo "The branch $BRANCH has commits that are not the robot's." >&2
        echo "result=foreign"
        exit 0
    fi
fi

# The pin is checked again on the fresh main: somebody may have bumped it
# during the wait.
pinned="$(mktemp)"
trap 'rm -f "$pinned"' EXIT
git show "origin/main:versions.json" > "$pinned"
state="$(python3 "$script_dir/steami-version.py" --released "$TAG" --search "$SEARCH" \
    --versions "$pinned" | sed -n 's/^state=//p')"
case "$state" in
    bump) ;;
    up-to-date)
        echo "main already pins STeaMi ${TAG#v} or a newer version." >&2
        echo "result=up-to-date"
        exit 0
        ;;
    *)
        echo "error: unexpected state \"$state\" on origin/main" >&2
        exit 1
        ;;
esac

git switch --quiet --force-create "$BRANCH" origin/main
python3 "$script_dir/steami-version.py" --released "$TAG" --search "$SEARCH" \
    --versions "$(git rev-parse --show-toplevel)/versions.json" --write > /dev/null
if git diff --quiet -- versions.json; then
    echo "error: versions.json unchanged after the bump" >&2
    exit 1
fi
git diff --stat >&2
git add versions.json
git commit --quiet -m "$TITLE"

# Only if the branch is still as checked above (absent, or at remote_sha).
git push --quiet "--force-with-lease=refs/heads/$BRANCH:$remote_sha" \
    "$push_url" "HEAD:refs/heads/$BRANCH"
echo "result=pushed"
