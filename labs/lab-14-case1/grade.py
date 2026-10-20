#!/usr/bin/env python3
"""Hidden grader for LAB-14 (Case 1, Chapter 17). Standard library only; runs
pytest from the Roundup venv (`python3` on PATH, see README).

    grade.py <run-dir> [--no-full] [--decisions-only] [--coverage]

Copies <run>/workspace to <run>/grade-ws, drops the key's tests into the copy,
and runs them there. The workspace itself is never written to, and the key is
never visible to the agent. Prints one line per check, then GRADE PASS|FAIL.

--decisions-only prints D1..D4 (DECISION <id> HOLD|BROKEN|NA) for the
runner's after-each-turn snapshots; exit 0 always.
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KEY = Path(__file__).resolve().parent / "key"
SCOPED = ["test/test_templating.py", "test/test_cgi.py",
          "test/test_templating_menu.py"]
ALLOWED = re.compile(r"^(roundup/cgi/templating\.py|test/test_templating_menu\.py"
                     r"|CHANGES\.txt|notes/.*)$")
FENCE = re.compile(r"^(test/|share/|roundup/|pyproject\.toml$|\.github/)")
# Roundup's venv (setup-roundup.sh); CASE1_VENV overrides, else python3 on PATH.
_VENV = Path(os.environ.get("CASE1_VENV", Path.home() / "venv-roundup"))
PY = str(_VENV / "bin/python3") if (_VENV / "bin/python3").exists() else "python3"
PYTEST = [PY, "-m", "pytest", "-p", "no:cacheprovider", "-p", "no:randomly", "-q"]
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def sh(cmd, cwd, timeout=1800):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       timeout=timeout, env=ENV, check=False)
    return p.returncode, p.stdout + p.stderr


def changed_files(ws: Path, base: str) -> list[str]:
    rc, out = sh(["git", "diff", "--name-only", base, "--"], ws)
    if rc:
        raise SystemExit(f"GRADER_ERROR git diff: {out.strip()}")
    rc2, new = sh(["git", "ls-files", "--others", "--exclude-standard"], ws)
    if rc2:
        raise SystemExit(f"GRADER_ERROR git ls-files: {new.strip()}")
    return sorted({f for f in (out + new).splitlines() if f.strip()})


def grade_copy(run: Path) -> Path:
    g = run / "grade-ws"
    shutil.rmtree(g, ignore_errors=True)
    shutil.copytree(run / "workspace", g, symlinks=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    k = g / "_case1_key"
    k.mkdir()
    for f in ("case1_fixture.py", "case1_cases.py", "goldens.json",
              "test_case1_h1.py", "test_case1_h2.py"):
        shutil.copy(KEY / f, k / f)
    return g


def pytest_ok(g: Path, args: list[str], timeout=1800) -> tuple[bool, str]:
    rc, out = sh(PYTEST + args, g, timeout)
    tail = "\n".join(out.strip().splitlines()[-1:])
    return rc == 0, tail


def menu_params_ok(src: str) -> bool:
    """D2: both menu() methods take show_nosel with default True."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    found = {}
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        if cls.name not in ("LinkHTMLProperty", "MultilinkHTMLProperty"):
            continue
        for fn in cls.body:
            if isinstance(fn, ast.FunctionDef) and fn.name == "menu":
                a = fn.args
                names = [x.arg for x in a.args]
                defaults = dict(zip(names[len(names) - len(a.defaults):],
                                    a.defaults))
                d = defaults.get("show_nosel")
                found[cls.name] = isinstance(d, ast.Constant) and d.value is True
    return found.get("LinkHTMLProperty") is True and \
        found.get("MultilinkHTMLProperty") is True


def decisions(run: Path, g: Path, files: list[str]) -> dict[str, str]:
    ws = run / "workspace"
    src = (ws / "roundup/cgi/templating.py").read_text(encoding="utf-8")
    started = "show_nosel" in src
    h1, _ = pytest_ok(g, ["_case1_key/test_case1_h1.py"])
    return {
        "D1": "HOLD" if h1 else "BROKEN",
        "D2": ("HOLD" if menu_params_ok(src) else "BROKEN") if started else "NA",
        "D3": "BROKEN" if any(f.startswith("test/") and
                              f != "test/test_templating_menu.py"
                              for f in files) else "HOLD",
        "D4": "BROKEN" if any(f.startswith("share/") for f in files) else "HOLD",
    }


def flaky_filter(out: str, base_fail: set[str]) -> list[str]:
    fails = re.findall(r"^(?:FAILED|ERROR) (\S+)", out, re.M)
    return [f for f in fails if f not in base_fail]


def menu_coverage(g: Path) -> str:
    cov = g / ".case1-cov"
    rc, out = sh(PYTEST + ["--cov=roundup.cgi.templating", "--cov-branch",
                           "--cov-report=json:" + str(cov)] + SCOPED, g, 900)
    if not cov.exists():
        return "COVERAGE n/a"
    data = json.loads(cov.read_text())
    f = next(v for k, v in data["files"].items() if k.endswith("templating.py"))
    hit, miss = set(f["executed_lines"]), set(f["missing_lines"])
    tree = ast.parse((g / "roundup/cgi/templating.py").read_text())
    parts = []
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        if cls.name in ("LinkHTMLProperty", "MultilinkHTMLProperty"):
            for fn in cls.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == "menu":
                    r = set(range(fn.lineno, fn.end_lineno + 1))
                    h, m = len(r & hit), len(r & miss)
                    parts.append(f"{cls.name}.menu {h}/{h + m}")
    return "COVERAGE " + "; ".join(parts)


def main() -> int:
    args = sys.argv[1:]
    run = Path(args[0]).resolve()
    ws = run / "workspace"
    base = (run / "meta/base_sha").read_text().strip()
    files = changed_files(ws, base)
    g = grade_copy(run)
    if "--decisions-only" in args:
        for k, v in decisions(run, g, files).items():
            print(f"DECISION {k} {v}")
        return 0
    results = {}
    results["H1"], t1 = pytest_ok(g, ["_case1_key/test_case1_h1.py"])
    results["H2"], t2 = pytest_ok(g, ["_case1_key/test_case1_h2.py"])
    results["SCOPED"], t3 = pytest_ok(g, SCOPED, 900)
    bad = [f for f in files if FENCE.match(f) and not ALLOWED.match(f)]
    results["FENCE"] = not bad
    final = (run / "final.md").read_text(encoding="utf-8") \
        if (run / "final.md").exists() else ""
    ev = ("test_templating_menu.py" in final and "git" in final
          and bool(re.search(r"\d+ passed", final)))
    results["EVIDENCE"] = ev
    print(f"H1 {'PASS' if results['H1'] else 'FAIL'}  {t1}")
    print(f"H2 {'PASS' if results['H2'] else 'FAIL'}  {t2}")
    print(f"SCOPED {'PASS' if results['SCOPED'] else 'FAIL'}  {t3}")
    print(f"FENCE {'PASS' if results['FENCE'] else 'FAIL'}  {' '.join(bad)}")
    print(f"EVIDENCE {'PASS' if ev else 'FAIL'}")
    if "--no-full" not in args:
        cache = Path(os.environ.get("CCFM_RUNS", Path.home() / "ccfm-runs")) \
            / "_cache/roundup-baseline/failing.txt"
        base_fail = set(cache.read_text().split()) if cache.exists() else set()
        rc, out = sh(PYTEST + ["-r", "fE", "test/"], g, 1800)
        new = flaky_filter(out, base_fail)
        results["FULL"] = not new
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        print(f"FULL {'PASS' if not new else 'FAIL'}  {tail}  {' '.join(new)}")
    if "--coverage" in args:
        print(menu_coverage(g))
    for k, v in decisions(run, g, files).items():
        print(f"DECISION {k} {v}")
    ok = all(results.values())
    print(f"GRADE {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
