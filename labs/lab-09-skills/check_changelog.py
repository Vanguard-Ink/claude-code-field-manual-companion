"""Check that a changelog was rolled for a release.

    python3 check_changelog.py <original> <rolled> <version> <created_utc>

Prints OK, or the first problem found.
"""

import re
import sys
from datetime import date, timedelta


def sections(text: str) -> dict[str, str]:
    """Map each '## [x]' heading line to the text under it."""
    parts = re.split(r"^(## \[.*)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def bullets(body: str) -> list[str]:
    return [ln.strip() for ln in body.splitlines() if ln.startswith("- ")]


def main() -> int:
    orig, rolled, version, created = sys.argv[1:5]
    a = sections(open(orig).read())
    b = sections(open(rolled).read())
    unreleased = a["## [Unreleased]"]
    if bullets(b.get("## [Unreleased]", "x")):
        print("Unreleased still has entries (or is missing)")
        return 1
    day = date.fromisoformat(created[:10])
    ok_days = {(day + timedelta(d)).isoformat() for d in (-1, 0, 1)}
    head = [h for h in b if h.startswith(f"## [{version}]")]
    if len(head) != 1:
        print(f"no single '## [{version}]' section")
        return 1
    m = re.fullmatch(rf"## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})", head[0])
    if not m or m.group(1) not in ok_days:
        print(f"bad heading or date: {head[0]!r}")
        return 1
    if bullets(b[head[0]]) != bullets(unreleased):
        print("entries changed, reordered, or missing")
        return 1
    for sub in ("### Added", "### Fixed"):
        if sub not in b[head[0]]:
            print(f"{sub} lost")
            return 1
    for h, body in a.items():
        if h != "## [Unreleased]" and b.get(h, "").strip() != body.strip():
            print(f"older section changed: {h}")
            return 1
    keys = list(b)
    if keys[:2] != ["## [Unreleased]", head[0]]:
        print("order: Unreleased, then the new release")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
