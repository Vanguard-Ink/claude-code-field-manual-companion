#!/usr/bin/env bash
# CI step from Chapter 18 (dod.yml): fence first, then
# the DoD, both from the PR's base commit. BASE = SHA.
set -euo pipefail
: "${BASE:?set BASE to the PR base SHA}"
: "${RUNNER_TEMP:=$(mktemp -d)}"
git cat-file -e "$BASE^{commit}"
git show "$BASE:.claude/dod.conf" \
  > "$RUNNER_TEMP/dod.conf"
. "$RUNNER_TEMP/dod.conf"
# Pytest takes its settings from the first of these
# it finds, and from every conftest.py on its path.
cfg=(pytest.toml .pytest.toml pytest.ini .pytest.ini
  pyproject.toml tox.ini setup.cfg
  ':(glob)**/conftest.py')
# $FENCE is unquoted on purpose: a path list.
changed=$(git diff --name-only "$BASE" HEAD \
  -- $FENCE "${cfg[@]}")
bad=$(printf '%s\n' "$changed" \
  | grep -vE "$FENCE_OK" | grep . || :)
[ -z "$bad" ] || { echo "$bad"; exit 1; }
eval "$DOD_CMD"
