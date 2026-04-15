#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_REMOTE="${UPSTREAM_REMOTE:-upstream}"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/sobbyellow/heroesrogue.git}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-master}"
PUSH_CHANGES=0
TARGET_BRANCH=""

usage() {
    cat <<'EOF'
Usage: ./scripts/sync_upstream.sh [--branch BRANCH] [--push]

Fetches the upstream Heroes Rogue repo, merges it into the current branch,
regenerates docs/ via scripts/generate_affix_overview.py, and optionally pushes
the result to origin.

Options:
  --branch BRANCH  Branch to sync and push. Defaults to the current branch.
  --push           Push the final branch state to origin.
  --help           Show this help text.

Environment:
  UPSTREAM_REMOTE  Remote name to use for the source repo. Default: upstream
  UPSTREAM_URL     Upstream Git URL. Default:
                   https://github.com/sobbyellow/heroesrogue.git
  UPSTREAM_BRANCH  Upstream branch to merge. Default: master
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --branch)
            if [[ $# -lt 2 ]]; then
                echo "--branch requires a value" >&2
                exit 1
            fi
            TARGET_BRANCH="$2"
            shift 2
            ;;
        --push)
            PUSH_CHANGES=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

cd "$ROOT_DIR"

CURRENT_BRANCH="$(git branch --show-current)"
if [[ -z "$CURRENT_BRANCH" ]]; then
    echo "Refusing to run from a detached HEAD checkout." >&2
    exit 1
fi

if [[ -z "$TARGET_BRANCH" ]]; then
    TARGET_BRANCH="$CURRENT_BRANCH"
fi

if [[ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]]; then
    echo "Current branch is $CURRENT_BRANCH, but target branch is $TARGET_BRANCH." >&2
    echo "Check out $TARGET_BRANCH first, then rerun the script." >&2
    exit 1
fi

if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
    echo "Working tree is not clean. Commit, stash, or remove local changes first." >&2
    exit 1
fi

if git remote get-url "$UPSTREAM_REMOTE" >/dev/null 2>&1; then
    EXISTING_UPSTREAM_URL="$(git remote get-url "$UPSTREAM_REMOTE")"
    if [[ "$EXISTING_UPSTREAM_URL" != "$UPSTREAM_URL" ]]; then
        git remote set-url "$UPSTREAM_REMOTE" "$UPSTREAM_URL"
    fi
else
    git remote add "$UPSTREAM_REMOTE" "$UPSTREAM_URL"
fi

echo "Fetching $UPSTREAM_REMOTE/$UPSTREAM_BRANCH..."
git fetch "$UPSTREAM_REMOTE" "$UPSTREAM_BRANCH"

echo "Merging $UPSTREAM_REMOTE/$UPSTREAM_BRANCH into $TARGET_BRANCH..."
git merge --no-edit "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH"

echo "Regenerating docs/..."
python3 scripts/generate_affix_overview.py

git add docs
if ! git diff --cached --quiet; then
    git commit -m "Regenerate affix overview"
else
    echo "No docs changes to commit."
fi

if [[ "$PUSH_CHANGES" -eq 1 ]]; then
    echo "Pushing to origin/$TARGET_BRANCH..."
    git push origin "$TARGET_BRANCH"
else
    echo "Sync complete. Review the result, then push when ready."
fi
