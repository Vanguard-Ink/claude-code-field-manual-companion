#!/usr/bin/env python3
"""Flag likely duplicates in code added since a base commit.

    python3 dupcheck.py --base <sha> [--canonical .claude/canonical.txt]

Three checks, all on non-test Python files changed since <base>:
  1. canonical: an added line matches a pattern that has a canonical
     helper elsewhere (canonical.txt), outside that helper's own file;
  2. name: a new top-level function reuses the name of an existing one
     in another file;
  3. shape: a new function's normalized AST is >= 80% similar to an
     existing function's.
Prints one finding per line; exits 1 if there are findings, else 0.
Heuristics, not proof: a finding is a question for the author.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import re
import subprocess
import sys
from pathlib import Path

SKIP = ("tests/", "/tests/", "clients/generated/", "vendor/", ".claude/")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def changed_files(base: str) -> list[str]:
    names = set(git("diff", "--name-only", base).split())
    names |= set(git("ls-files", "--others", "--exclude-standard").split())
    return sorted(n for n in names if n.endswith(".py") and Path(n).exists()
                  and not any(s in f"/{n}" for s in SKIP))


def in_base(base: str, path: str) -> bool:
    return git("cat-file", "-t", f"{base}:{path}").strip() == "blob"


def added_lines(base: str, path: str) -> list[str]:
    if not in_base(base, path):
        return Path(path).read_text().splitlines()
    diff = git("diff", "-U0", base, "--", path)
    return [ln[1:] for ln in diff.splitlines()
            if ln.startswith("+") and not ln.startswith("+++")]


def functions(src: str, top_only: bool = False) -> dict[str, str]:
    """Functions (all, or top-level only) -> normalized AST dump."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    out = {}
    for node in (tree.body if top_only else ast.walk(tree)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = ast.Module(body=node.body, type_ignores=[])
            dump = ast.dump(body, annotate_fields=False)
            dump = re.sub(r"Name\('[^']*'", "Name('v'", dump)
            dump = re.sub(r"arg\('[^']*'", "arg('a'", dump)
            out[node.name] = dump
    return out


def base_functions(base: str) -> dict[tuple[str, str], str]:
    out = {}
    for path in git("ls-tree", "-r", "--name-only", base).split():
        if path.endswith(".py") and path.startswith("packages/") \
                and not any(s in f"/{path}" for s in SKIP):
            for name, dump in functions(git("show", f"{base}:{path}")).items():
                out[(path, name)] = dump
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--canonical", default=".claude/canonical.txt")
    a = ap.parse_args()
    rules: list[tuple[re.Pattern[str], str, str]] = []
    if Path(a.canonical).exists():
        for ln in Path(a.canonical).read_text().splitlines():
            if ln.strip() and not ln.startswith("#"):
                raw, helper, home = ln.split("\t")
                rules.append((re.compile(raw), helper, home))
    old = base_functions(a.base)
    old_names: dict[str, str] = {}
    for path in {p for p, _ in old}:
        for name in functions(git("show", f"{a.base}:{path}"), top_only=True):
            old_names.setdefault(name, path)
    findings: list[str] = []
    for path in changed_files(a.base):
        for line in added_lines(a.base, path):
            for pat, helper, home in rules:
                comment = line.lstrip().startswith("#")
                if path != home and pat.search(line) and not comment:
                    findings.append(
                        f"canonical: {path}: `{line.strip()}` -> reuse {helper}")
        before = (functions(git("show", f"{a.base}:{path}"))
                  if in_base(a.base, path) else {})
        for name, dump in functions(Path(path).read_text()).items():
            if name in before or name.startswith("test_"):
                continue
            top = name in functions(Path(path).read_text(), top_only=True)
            if top and name in old_names and old_names[name] != path \
                    and not name.startswith("_"):
                findings.append(
                    f"name: {path}: {name}() also defined in {old_names[name]}")
            for (opath, oname), odump in old.items():
                if opath == path or len(dump) < 200:
                    continue
                r = difflib.SequenceMatcher(None, dump, odump).ratio()
                if r >= 0.8:
                    findings.append(f"shape: {path}: {name}() is {r:.0%}"
                                    f" like {opath}:{oname}()")
    for f in dict.fromkeys(findings):
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
