"""Scope, public-name, and size checks for a LAB-10 run.

    python3 drift.py <workspace> <base-sha> <task-dir>

Prints lines "name|description|PASS or FAIL" for grade.sh.
"""

import ast
import difflib
import subprocess
import sys
from pathlib import Path

ws, base, task = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
SAMPLE = Path(__file__).resolve().parents[2] / "sample-app"


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ws), *a], capture_output=True, text=True).stdout


changed = sorted(set(git("diff", "--name-only", base).split())
                 | set(git("ls-files", "--others", "--exclude-standard").split()))
changed = [c for c in changed if c != ".claude/dod-base"]
is_test = lambda p: "/tests/" in f"/{p}"  # noqa: E731

scope = [s for s in (task / "scope.txt").read_text().split() if s]
outside = [c for c in changed if not any(c == s or c.startswith(s) for s in scope)
           and not c.startswith("notes/")]
print(f"scope|{'within Scope list' if not outside else 'outside: ' + ' '.join(outside)[:40]}"
      f"|{'PASS' if not outside else 'FAIL'}")


def public(src: str) -> set[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    names = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, ast.Assign):
            names |= {t.id for t in n.targets if isinstance(t, ast.Name)}
    return {x for x in names if not x.startswith("_") and not x.isupper()}


allowed = set((task / "allow_public.txt").read_text().split())
new_public = set()
for c in changed:
    if c.endswith(".py") and not is_test(c) and (ws / c).exists():
        before = git("show", f"{base}:{c}") if git("cat-file", "-t", f"{base}:{c}").strip() else ""
        new_public |= public((ws / c).read_text()) - public(before)
extra = sorted(new_public - allowed)
print(f"public|{'no unrequested public names' if not extra else 'new: ' + ', '.join(extra)[:44]}"
      f"|{'PASS' if not extra else 'FAIL'}")


def added(old: str, new: str) -> int:
    return sum(1 for ln in difflib.ndiff(old.splitlines(), new.splitlines())
               if ln.startswith("+ ") and ln[2:].strip())


ref = 0
for f in (task / "reference").rglob("*.py"):
    rel = f.relative_to(task / "reference")
    old = (SAMPLE / rel).read_text() if (SAMPLE / rel).exists() else ""
    ref += added(old, f.read_text())
got = 0
for c in changed:
    if c.endswith(".py") and not is_test(c) and (ws / c).exists():
        before = git("show", f"{base}:{c}") if git("cat-file", "-t", f"{base}:{c}").strip() else ""
        got += added(before, (ws / c).read_text())
ratio = got / max(ref, 1)
bloat = ratio > 3 and got - ref > 15
print(f"size|{got} lines added vs {ref} in reference ({ratio:.1f}x)|{'FAIL' if bloat else 'PASS'}")
