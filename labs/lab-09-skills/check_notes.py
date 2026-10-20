"""Check release notes: headings in order, checks with exit codes, entries.

    python3 check_notes.py <notes.md> <version> <original-changelog>
"""

import re
import sys

notes, version, changelog = sys.argv[1:4]
text = open(notes).read()
heads = [ln.strip() for ln in text.splitlines() if ln.startswith("#")]
want = [f"# Release {version}", "## Checks", "## Changes", "## Not done"]
if [h for h in heads if h in want] != want or heads[0] != want[0]:
    sys.exit(f"headings: {heads}")
checks = text.split("## Checks", 1)[1].split("## Changes", 1)[0]
for cmd in ("make test", "make lint", "make typecheck"):
    if not re.search(rf"{cmd}\b.*\b0\b", checks):
        sys.exit(f"no exit code for {cmd}")
changes = text.split("## Changes", 1)[1].split("## Not done", 1)[0]
unrel = open(changelog).read().split("## [Unreleased]", 1)[1].split("## [", 1)[0]
for b in (ln[2:].strip() for ln in unrel.splitlines() if ln.startswith("- ")):
    if b not in changes:
        sys.exit(f"missing entry: {b}")
nd = text.split("## Not done", 1)[1].lower()
if not all(w in nd for w in ("tag", "push", "publish")):
    sys.exit("Not done must list tag, push, publish")
