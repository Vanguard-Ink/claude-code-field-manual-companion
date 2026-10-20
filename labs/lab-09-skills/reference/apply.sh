#!/bin/bash
# Self-test only: apply a correct release to a LAB-09 workspace.
#   reference/apply.sh <workspace> <yyyy-mm-dd>
set -eu
WS=$1; D=$2; HERE=$(cd "$(dirname "$0")" && pwd)
cp "$HERE/VERSION" "$WS/VERSION"
cp "$HERE/packages/shared/ledgerline_shared/version.py" \
   "$WS/packages/shared/ledgerline_shared/version.py"
python3 - "$WS/CHANGELOG.md" "$D" <<'PY'
import sys
p, d = sys.argv[1:3]
t = open(p).read()
t = t.replace("## [Unreleased]\n", f"## [Unreleased]\n\n## [0.5.0] - {d}\n", 1)
open(p, "w").write(t)
PY
mkdir -p "$WS/release"
cp "$HERE/release/0.5.0.md" "$WS/release/0.5.0.md"
