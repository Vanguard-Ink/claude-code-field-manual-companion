#!/usr/bin/env python3
"""Run the book's labs headless with `claude -p` and record what they cost.

    python3 tools/run-labs.py [--labs 01,02,...] [--dry] [--model sonnet] [--effort medium]

Every run gets a fresh workspace from tools/new-run.sh, a clean Claude Code
environment (no inherited config, plugins, MCP servers, or parent-session
variables), and its full stream-json transcript is kept. Results go to
$CCFM_RUNS/_results/: one CSV per lab, a usage ledger, and summary.md.

The runner is resumable: finished runs are recorded in state.json and skipped.
If Claude Code reports a usage limit, the runner saves state and exits with
code 75 so the caller can resume after the limit resets.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = Path(os.environ.get("CCFM_RUNS", Path.home() / "ccfm-runs"))
OUT = RUNS / "_results"
STATE = OUT / "state.json"
CONFIG_DIR = RUNS / "_claude-config"
LIMIT_EXIT = 75
MODEL = "sonnet"  # set from --model in main()
RUN_TIMEOUT = 45 * 60

KEEP_ENV = [
    "PATH", "HOME", "LANG", "LC_ALL", "TERM", "HTTPS_PROXY", "HTTP_PROXY",
    "https_proxy", "http_proxy", "NO_PROXY", "no_proxy", "NODE_EXTRA_CA_CERTS",
    "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CLAUDE_SESSION_INGRESS_TOKEN_FILE",
    "SESSION_INGRESS_URL",  # no account email or UUID: they leaked into transcripts
    "CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST", "ANTHROPIC_API_KEY",
    "CLAUDE_CODE_OAUTH_TOKEN", "VIRTUAL_ENV",
]


# Tools a lab agent may use without asking. Everything else is denied
# (dontAsk). Exact commands only: no interpreter wildcards (python3 *),
# no find/cp/mv, and no Agent tool except where a variant needs it
# (LAB-05 delegated, LAB-08 code-review). Never add
# --dangerously-skip-permissions or bypassPermissions.
ALLOWED_TOOLS = [
    "Read", "Grep", "Glob", "Edit", "Write", "TodoWrite",
    "Bash(make test)", "Bash(make lint)", "Bash(make typecheck)",
    "Bash(make lint typecheck)", "Bash(make test lint typecheck)",
    "Bash(python3 -m pytest *)", "Bash(python3 -m pytest)", "Bash(python -m pytest *)",
    "Bash(git status *)", "Bash(git status)", "Bash(git diff *)", "Bash(git diff)",
    "Bash(git log *)", "Bash(git show *)", "Bash(git add *)", "Bash(git commit *)",
    "Bash(git rm *)", "Bash(ls *)", "Bash(ls)", "Bash(cat *)", "Bash(head *)",
    "Bash(tail *)", "Bash(wc *)", "Bash(grep *)", "Bash(date *)", "Bash(mkdir *)",
]
NEEDS_AGENT = {("lab-05", "delegated"), ("lab-08", "code-review"), ("lab-14", "method")}
# The main-session baseline must not delegate: its agent file stays (same
# session start as `delegated`), but calling it is denied.
DENY_AGENT = {("lab-05", "main"): "Agent(code-locator)", ("lab-14", "baseline"): "Agent"}
# LAB-11 part B gives both variants a push permission, so the only difference
# between `open` and `policy` is the committed deny rules (deny beats allow).
EXTRA_ALLOW = {("lab-11", "open"): ["Bash(git push *)", "Bash(git push)"],
               ("lab-11", "policy"): ["Bash(git push *)", "Bash(git push)"]}


class LimitHit(Exception):
    pass


# ---------------------------------------------------------------- utilities
def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# Told to every lab agent, identically in every variant, so a check it is
# allowed to run never fails on shell syntax the allowlist doesn't cover.
ENV_NOTE = ("Lab environment: Bash runs only plain commands from an allowlist "
            "(make test, make lint typecheck, python3 -m pytest, git, ls, cat, "
            "grep, head, tail, wc). Pipes, redirects, heredocs, shell variables, "
            "and inline python are blocked. Run each check exactly as written in "
            "the task's DONE.md and edit files with the Edit or Write tool. "
            "The repository already has a lab git identity: commit with plain "
            "`git commit`, never with a personal name or email.")


def prepare_config() -> None:
    """Keep the runner's Claude Code config free of account-synced extras."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    f = CONFIG_DIR / "settings.json"
    cfg = json.loads(f.read_text()) if f.exists() else {}
    cfg.update(syncClaudeAiSkills=False, syncClaudeAiPlugins=False)
    f.write_text(json.dumps(cfg, indent=2))


def preflight() -> None:
    """Refuse to run if account skills or plugins still load (they skew results)."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        rep = context_start(Path(d)).get("context_report", "")
    bad = [ln for ln in rep.splitlines() if "claude.ai sync" in ln or "| Plugin (" in ln]
    if not rep:
        sys.exit("preflight: /context failed (not logged in? see guide step 4)")
    if bad:
        sys.exit("preflight: account skills/plugins still load in the runner config:\n"
                 + "\n".join(bad[:5]) + "\nStart claude once with "
                 "CLAUDE_CONFIG_DIR=$HOME/ccfm-runs/_claude-config, type /exit, retry.")
    print("preflight: clean config (no synced skills or plugins)", flush=True)


def clean_env() -> dict[str, str]:
    env = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    env.update(CLAUDE_CODE_SYNC_PLUGINS="0", CLAUDE_CONFIG_DIR=str(CONFIG_DIR),
               CCFM_RUNS=str(RUNS),
               CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL="1")
    return env


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"done": {}}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=1))


def new_run(lab: str, variant: str, item: str = "") -> Path:
    args = [str(ROOT / "tools/new-run.sh"), lab, variant] + ([item] if item else [])
    p = subprocess.run(args, check=True, capture_output=True, text=True,
                       env={**os.environ, "CCFM_RUNS": str(RUNS)})
    return Path(re.search(r"Run created: (.+)", p.stdout).group(1).strip())


def sh(cmd: list[str] | str, cwd: Path, timeout: int = 600) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       shell=isinstance(cmd, str), env={**os.environ})
    return p.returncode, p.stdout + p.stderr


class Session:
    """One Claude Code conversation (one or more `claude -p` calls)."""

    def __init__(self, run: Path, args, cwd: Path | None = None, extra: list[str] | None = None,
                 env: dict[str, str] | None = None, strict_mcp: bool = True):
        self.run, self.args = run, args
        self.cwd = cwd or run / "workspace"
        self.extra = extra or []
        self.env = env or {}
        # strict_mcp=False lets a run load the project's .mcp.json, as a plain
        # `claude -p` in CI would (LAB-12 part C). Every other run is strict.
        self.strict_mcp = strict_mcp
        meta = run / "meta"
        key = ((meta / "lab").read_text().strip(), (meta / "variant").read_text().strip()) \
            if (meta / "lab").exists() else ("", "")
        self.tools = (ALLOWED_TOOLS + (["Agent"] if key in NEEDS_AGENT else [])
                      + EXTRA_ALLOW.get(key, []))
        self.deny = DENY_AGENT.get(key)
        self.sid: str | None = None
        self.turns: list[dict] = []
        (run / "transcripts").mkdir(exist_ok=True)

    def ask(self, prompt: str, plan: bool = False, label: str = "") -> dict:
        cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--model", self.args.model, "--effort", self.args.effort,
               "--no-chrome"]
        if self.strict_mcp:
            cmd += ["--strict-mcp-config"]
            cmd += [] if "--mcp-config" in self.extra else ["--mcp-config", '{"mcpServers":{}}']
        cmd += self.extra
        # Scoped, pre-approved tools only; anything else is denied (dontAsk).
        # No --dangerously-skip-permissions: lab agents never get unrestricted access.
        cmd += ["--permission-mode", "plan" if plan else "dontAsk",
                "--allowedTools", ",".join(self.tools),
                "--append-system-prompt", ENV_NOTE]
        if self.deny:
            cmd += ["--disallowedTools", self.deny]
        if self.sid:
            cmd += ["--resume", self.sid]
        n = len(self.turns) + 1
        log = self.run / "transcripts" / f"turn{n:02d}{('-' + label) if label else ''}.jsonl"
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True,
                               timeout=RUN_TIMEOUT, env={**clean_env(), **self.env})
            raw, code = p.stdout, p.returncode
        except subprocess.TimeoutExpired as e:
            raw = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            code = None
        log.write_text(raw)
        turn = parse_stream(raw)
        turn["exit_code"] = code
        turn.update(prompt=prompt[:200], label=label, wall_s=round(time.time() - t0, 1))
        if turn.get("limit"):
            raise LimitHit(turn.get("result", "")[:300])
        apply_delta(turn, self.turns, self.sid)
        self.sid = turn.get("session_id") or self.sid
        self.turns.append(turn)
        return turn

    def total(self, key: str) -> float:
        return sum(t.get(key, 0) or 0 for t in self.turns)


def apply_delta(turn: dict, turns: list[dict], sid: str | None) -> None:
    """Per-call usage = this call's cumulative session total minus the previous call's."""
    cum = turn.pop("cum", None) or {}
    prev = turns[-1].get("cum_after", {}) if turns and turn.get("session_id") == sid else {}
    for k in ("input_tokens", "output_tokens", "cache_read", "cache_write", "other_model_tokens", "cost_usd"):
        turn[k] = max((cum.get(k) or 0) - (prev.get(k) or 0), 0)
    turn["cost_usd"] = round(turn["cost_usd"], 6)
    turn["total_tokens"] = (turn["input_tokens"] + turn["output_tokens"]
                            + turn["cache_read"] + turn["cache_write"])
    turn["cum_after"] = cum or prev


def parse_stream(raw: str) -> dict:
    out: dict = {"tools": {}, "gate_blocks": 0, "context_tokens": 0}
    result = None
    for line in raw.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            msg = ev.get("message", {})
            u = msg.get("usage") or {}
            ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                   + u.get("cache_creation_input_tokens", 0))
            if ctx and not ev.get("parent_tool_use_id"):
                out["context_tokens"] = ctx
            for c in msg.get("content", []):
                if c.get("type") == "tool_use":
                    out["tools"][c["name"]] = out["tools"].get(c["name"], 0) + 1
        if "DoD gate (" in line:
            out["gate_blocks"] += line.count("DoD gate (")
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            out["init"] = {k: ev.get(k) for k in ("mcp_servers", "mcp_server_errors", "plugin_errors",
                                                  "permissionMode", "tools") if k in ev}
        if ev.get("type") == "result":
            result = ev
    if result is None:
        out.update(is_error=True, result="no result event (timeout or crash)")
        return out
    # `modelUsage` and `total_cost_usd` are cumulative for the whole session
    # (a --resume keeps counting) and include subagents, /compact and bundled
    # commands such as /code-review. `usage` covers only the main loop, so it
    # is used only as a fallback. Session.ask turns these into per-call deltas.
    u = result.get("usage") or {}
    mu = result.get("modelUsage") or {}
    text = result.get("result") or ""
    if mu:
        cum = {"input_tokens": sum(v.get("inputTokens", 0) for v in mu.values()),
               "output_tokens": sum(v.get("outputTokens", 0) for v in mu.values()),
               "cache_read": sum(v.get("cacheReadInputTokens", 0) for v in mu.values()),
               "cache_write": sum(v.get("cacheCreationInputTokens", 0) for v in mu.values())}
        main = next((m for m in mu if MODEL in m), max(mu, key=lambda m: mu[m].get("outputTokens", 0)))
        cum["other_model_tokens"] = sum(
            v.get("inputTokens", 0) + v.get("outputTokens", 0) + v.get("cacheReadInputTokens", 0)
            + v.get("cacheCreationInputTokens", 0) for m, v in mu.items() if m != main)
    else:
        cum = {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
               "cache_read": u.get("cache_read_input_tokens", 0),
               "cache_write": u.get("cache_creation_input_tokens", 0), "other_model_tokens": 0}
    cum["cost_usd"] = result.get("total_cost_usd") or 0.0
    out.update(
        session_id=result.get("session_id"), is_error=bool(result.get("is_error")),
        result=text, num_turns=result.get("num_turns") or 0,
        cum=cum, models=sorted(mu), subtype=result.get("subtype"),
        structured_output=result.get("structured_output"),
        denials=[d.get("tool_input") for d in result.get("permission_denials") or []],
    )
    errs = " ".join(str(e) for e in result.get("errors") or [])
    lim = re.search(r"usage limit|limit reached|rate limit|hit your .*limit|429", text + " " + errs, re.I)
    # A run stopped by its own --max-turns / --max-budget-usd cap is a result
    # (LAB-12), not a plan usage limit.
    capped = str(out.get("subtype") or "").startswith("error_max")
    out["limit"] = bool(out["is_error"] and lim and not capped)
    return out


def context_start(cwd: Path, extra: list[str] | None = None) -> dict:
    """Session-start budget from a headless /context (no model request)."""
    cmd = ["claude", "-p", "/context", "--output-format", "json", "--no-chrome",
           "--append-system-prompt", ENV_NOTE,
           "--strict-mcp-config", "--model", MODEL]
    cmd += extra or ["--mcp-config", '{"mcpServers":{}}']
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300, env=clean_env())
    try:
        text = json.loads(p.stdout)["result"]
    except Exception:  # noqa: BLE001
        return {"start_tokens": None, "start_breakdown": p.stdout[:300]}
    m = re.search(r"\*\*Tokens:\*\* ([\d.]+)k", text)
    cats = dict(re.findall(r"^\| ([A-Z][\w ()]+?) \| ([\d.]+k?) \|", text, re.M))
    return {"start_tokens": float(m.group(1)) * 1000 if m else None,
            "start_breakdown": "; ".join(f"{k}={v}" for k, v in cats.items()),
            "context_report": text}


# ---------------------------------------------------------------- recording
LEDGER_FIELDS = ["date_utc", "lab", "run_key", "variant", "item", "turns", "calls",
                 "total_tokens", "input_tokens", "output_tokens", "cache_read",
                 "cache_write", "other_model_tokens", "cost_usd_list_price", "wall_s"]


def record(lab: str, key: str, row: dict, sess: Session | list[Session] | None, state: dict) -> None:
    sessions = sess if isinstance(sess, list) else ([sess] if sess else [])
    turns = [t for s in sessions for t in s.turns]
    usage = {
        "turns": sum(t.get("num_turns", 0) for t in turns), "calls": len(turns),
        "total_tokens": sum(t.get("total_tokens", 0) for t in turns),
        "input_tokens": sum(t.get("input_tokens", 0) for t in turns),
        "output_tokens": sum(t.get("output_tokens", 0) for t in turns),
        "cache_read": sum(t.get("cache_read", 0) for t in turns),
        "cache_write": sum(t.get("cache_write", 0) for t in turns),
        "other_model_tokens": sum(t.get("other_model_tokens", 0) for t in turns),
        "cost_usd_list_price": round(sum(t.get("cost_usd", 0) for t in turns), 4),
        "wall_s": round(sum(t.get("wall_s", 0) for t in turns), 1),
    }
    full = {"date_utc": now(), "lab": lab, "run_key": key, **row, **usage}
    OUT.mkdir(parents=True, exist_ok=True)
    for path, fields in ((OUT / f"{lab}.csv", list(full)), (OUT / "usage-ledger.csv", LEDGER_FIELDS)):
        new = not path.exists()
        if not new:  # rows of one lab can have different fields: widen the header
            with path.open(newline="") as f:
                old = list(csv.DictReader(f))
                head = list(old[0].keys()) if old else fields
            union = head + [k for k in fields if k not in head]
            if union != head:
                with path.open("w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=union)
                    w.writeheader(); w.writerows(old)
            fields = union
        with path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            if new:
                w.writeheader()
            w.writerow(full)
    state["done"][key] = full
    save_state(state)
    print(f"[{now()}] {key}: {usage['total_tokens']:,} tokens, ${usage['cost_usd_list_price']}", flush=True)


def task_text(ws: Path, pattern: str) -> str:
    return next(ws.glob(pattern)).read_text()


def keywords(text: str, groups: list[list[str]]) -> int:
    t = text.lower()
    return sum(1 for g in groups if any(k.lower() in t for k in g))


# ---------------------------------------------------------------- labs
def lab01(args, state):
    lab = "lab-01"
    key = f"{lab}/start"
    if key not in state["done"]:
        run = new_run(lab, "base")
        cs = context_start(run / "workspace")
        (run / "context.md").write_text(cs.pop("context_report", ""))
        record(lab, key, {"variant": "base", "item": "start", **cs}, None, state)
    for t, glob in (("A", "tasks/A-*/TASK.md"), ("B", "tasks/B-*/TASK.md"), ("C", "tasks/C-*/TASK.md")):
        key = f"{lab}/{t}"
        if key in state["done"]:
            continue
        run = new_run(lab, "base")
        ws = run / "workspace"
        s = Session(run, args)
        r = s.ask(task_text(ws, glob), label=t)
        (run / "final.md").write_text(r.get("result", ""))
        if t == "A":
            ok = sh("python3 -m pytest -q tests/acceptance/test_a_roles.py && make test lint typecheck", ws)[0] == 0
        elif t == "B":
            ok = keywords(r.get("result", ""), [["correct", "fine", "no blocker", "no bug", "looks good", "no issue"]]) == 1
        else:
            ok = keywords(r.get("result", ""), [["grace"], ["prorat"], ["minimum"], ["float"]]) == 4
        record(lab, key, {"variant": "base", "item": t, "pass": ok,
                          "end_context_tokens": r.get("context_tokens"),
                          "cache_hit_share": round(r.get("cache_read", 0) / max(1, r.get("cache_read", 0) + r.get("cache_write", 0) + r.get("input_tokens", 0)), 3)}, s, state)


PROBES = {
    "P1": "Add `apply_discount(amount, percent)` to the billing package.",
    "P2": "The docstring of `get_report` in `clients/generated/ledgerline_client/api.py` says \"Get\". Change it to \"Fetch\".",
    "P3": "Add a `currency` column to the invoices table.",
    "P4": "Add a web handler that lists reports page by page.",
    "P5": "Make a small fix of your choice in reports and commit it.",
}


def lab02(args, state):
    lab = "lab-02"
    for variant in ("before", "after"):
        key = f"{lab}/{variant}/start"
        if key not in state["done"]:
            run = new_run(lab, variant)
            ws = run / "workspace"
            extra = ["--mcp-config", str(ws / ".mcp.json")] if (ws / ".mcp.json").exists() else None
            cs = context_start(ws, extra)
            (run / "context.md").write_text(cs.pop("context_report", ""))
            record(lab, key, {"variant": variant, "item": "start", **cs}, None, state)
        for p, prompt in PROBES.items():
            key = f"{lab}/{variant}/{p}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant)
            ws = run / "workspace"
            extra = ["--mcp-config", str(ws / ".mcp.json")] if (ws / ".mcp.json").exists() else None
            s = Session(run, args, extra=extra)
            r = s.ask(prompt, label=p)
            (run / "final.md").write_text(r.get("result", ""))
            code, out = sh([str(ROOT / "labs/lab-02-session-start/check-probe.sh"), str(run), p], ws)
            verdict = "FOLLOWED" if "FOLLOWED" in out else ("BROKEN" if "BROKEN" in out else "NOT ATTEMPTED")
            record(lab, key, {"variant": variant, "item": p, "verdict": verdict}, s, state)


def lab03(args, state):
    lab = "lab-03"
    key = f"{lab}/long"
    if key not in state["done"]:
        run = new_run(lab, "long")
        ws = run / "workspace"
        s = Session(run, args)
        per = []
        for t, glob in (("A", "tasks/A-*/TASK.md"), ("B", "tasks/B-*/TASK.md"), ("C", "tasks/C-*/TASK.md")):
            r = s.ask(task_text(ws, glob), label=t)
            per.append(f"{t}:{r.get('context_tokens')}")
        a_ok = sh("python3 -m pytest -q tests/acceptance/test_a_roles.py && make test lint typecheck", ws)[0] == 0
        record(lab, key, {"variant": "long", "item": "A+B+C", "context_after_each": " ".join(per), "task_a_pass": a_ok}, s, state)
    key = f"{lab}/cleared"
    if key not in state["done"]:
        sessions, per = [], []
        a_ok = None
        for t, glob in (("A", "tasks/A-*/TASK.md"), ("B", "tasks/B-*/TASK.md"), ("C", "tasks/C-*/TASK.md")):
            run = new_run(lab, "cleared")
            ws = run / "workspace"
            s = Session(run, args)
            r = s.ask(task_text(ws, glob), label=t)
            per.append(f"{t}:{r.get('context_tokens')}")
            if t == "A":
                a_ok = sh("python3 -m pytest -q tests/acceptance/test_a_roles.py && make test lint typecheck", ws)[0] == 0
            sessions.append(s)
        record(lab, key, {"variant": "cleared", "item": "A+B+C", "context_after_each": " ".join(per), "task_a_pass": a_ok}, sessions, state)


RECITE = ("Before you continue: restate the decisions in notes/handoff.md, "
          "the next open item, and the last proof of done. Then stop.")


def lab04(args, state):
    lab = "lab-04"
    grade = ROOT / "labs/lab-04-compaction/grade.sh"
    task = "tasks/R01-retry-refactor/TASK.md"
    for variant in ("default", "designed", "restart"):
        key = f"{lab}/{variant}"
        if key in state["done"]:
            continue
        run = new_run(lab, "default" if variant == "default" else "designed", "R01")
        ws = run / "workspace"
        designed = variant != "default"
        upd = " Update notes/handoff.md after each step." if designed else ""
        sessions = [Session(run, args)]
        s = sessions[0]
        if designed:
            s.ask(f"Read {task} and its DONE.md and make a six-step plan. Don't edit files.", plan=True, label="plan")
        s.ask(f"Do steps 1 and 2 of {task}. Run `make test lint typecheck` after each step.{upd} Then stop.", label="steps1-2")
        if variant == "restart":
            s = Session(run, args)
            sessions.append(s)
            s.ask(f"Read notes/handoff.md and {task}. Continue with steps 3 and 4. Run `make test lint typecheck` after each step.{upd} Then stop.", label="steps3-4-fresh")
        else:
            s.ask("/compact", label="compact1")
            if designed:
                s.ask(RECITE, label="recite1")
            s.ask(f"Do steps 3 and 4 of {task}. Run `make test lint typecheck` after each step.{upd} Then stop.", label="steps3-4")
        s.ask("/compact", label="compact2")
        if designed:
            s.ask(RECITE, label="recite2")
        r = s.ask(f"Do steps 5 and 6 of {task}. Then run the checks in its DONE.md and report with the evidence it asks for.", label="steps5-6")
        (run / "final.md").write_text(r.get("result", ""))
        code, out = sh([str(grade), str(run)], ws)
        rounds = 0
        while code != 0 and rounds < 2:
            rounds += 1
            r = s.ask(f"A grader checked your work and reports:\n\n{out}\n\nFix what failed, rerun the checks, and report with evidence.", label=f"correction{rounds}")
            (run / "final.md").write_text(r.get("result", ""))
            code, out = sh([str(grade), str(run)], ws)
        (run / "grade.txt").write_text(out)
        rev = re.search(r"REVERSED_DECISIONS (\d+)", out)
        record(lab, key, {"variant": variant, "item": "R01", "grade": "PASS" if code == 0 else "FAIL",
                          "reversed_decisions": int(rev.group(1)) if rev else None,
                          "correction_rounds": rounds,
                          "compactions": 1 if variant == "restart" else 2}, sessions, state)


L5_KEY = [
    [["permissions.py"], ["can_export"], ["viewer_export", "is_enabled", "flags.py"]],
    [["retry_helper"], ["ConnectionError"], ["GatewayTimeout", "not retried", "isn't retried", "not retr"]],
    [["settings.py", "nightly_run_hour"], ["next_run_at", "invoices.py"]],
    [["fees.py"], ["compute_late_fee"], ["0.5", "minimum"]],
    [["handle_get_report", "handlers.py"], ["get_report", "service.py"], ["KeyError"]],
]


def lab05(args, state):
    lab = "lab-05"
    qs = re.findall(r"^\d\. (.+?)(?=^\d\. |\Z)", (ROOT / "labs/lab-05-subagents/questions.md").read_text(), re.S | re.M)
    qs = [" ".join(q.split()) for q in qs]
    for variant in ("main", "delegated"):
        key = f"{lab}/{variant}"
        if key in state["done"]:
            continue
        run = new_run(lab, variant)
        s = Session(run, args)
        scores, ctx = [], []
        for i, q in enumerate(qs, 1):
            prompt = q.replace("(Follow-up, unrelated) ", "")
            if variant == "delegated" and i <= 5:
                prompt = "@agent-code-locator " + prompt
            r = s.ask(prompt, label=f"q{i}")
            ctx.append(r.get("context_tokens"))
            if i <= 5:
                txt = r.get("result", "")
                hit = keywords(txt, L5_KEY[i - 1])
                score = (1 if hit >= 1 else 0) + (1 if hit == len(L5_KEY[i - 1]) else 0) + (1 if re.search(r"\.py:\d+|\.py\b", txt) else 0)
                scores.append(score)
        record(lab, key, {"variant": variant, "item": "Q1-6", "scores_q1_5": " ".join(map(str, scores)),
                          "score_total": sum(scores), "context_after_each": " ".join(map(str, ctx)),
                          "q6_tokens": s.turns[-1].get("total_tokens"),
                          "subagent_calls": sum(t["tools"].get("Agent", 0) + t["tools"].get("Task", 0) for t in s.turns)}, s, state)


L6_KEY = {"L1": [["fees.py"], ["compute_late_fee"], ["float"], ["round"]],
          "L2": [["charge"], ["retry_helper", "with_retries"], ["attempts"], ["3"]]}


def lab06(args, state):
    lab = "lab-06"
    grade = ROOT / "labs/lab-06-legacy/grade.sh"
    for variant in ("default", "scoped"):
        for item in ("L1", "L2", "L3"):
            key = f"{lab}/{variant}/{item}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant, item)
            ws = run / "workspace"
            cwd = ws / "packages/billing" if variant == "scoped" else ws
            cs = context_start(cwd)
            (run / "context.md").write_text(cs.pop("context_report", ""))
            s = Session(run, args, cwd=cwd)
            tdir = next(ws.glob(f"tasks/{item}-*"))
            prompt = (tdir / "TASK.md").read_text()
            if item == "L3":
                prompt += "\nCommit the characterization tests on their own before changing fees.py, then commit the fix."
            r = s.ask(prompt, label=item)
            (run / "final.md").write_text(r.get("result", ""))
            row = {"variant": variant, "item": item, **cs,
                   "files_read": sum(t["tools"].get("Read", 0) for t in s.turns),
                   "searches": sum(t["tools"].get("Grep", 0) + t["tools"].get("Glob", 0) for t in s.turns)}
            if item == "L3":
                code, out = sh([str(grade), str(run)], ws)
                (run / "grade.txt").write_text(out)
                cov = re.search(r"characterization \((\d+)%\)", out)
                row.update(grade="PASS" if code == 0 else "FAIL", fees_coverage_pct=cov.group(1) if cov else None)
            else:
                row.update(score=f"{keywords(r.get('result', ''), L6_KEY[item])}/4")
            record(lab, key, row, s, state)


NOT_DONE = re.compile(r"isn't done|is not done|not done yet|couldn't run|could not run|"
                      r"unable to run|blocked|haven't run|have not run", re.I)

LAB07_PROMPT = ("Do the task in {task}/TASK.md. Run the checks in its DONE.md and "
                "show their output before you say you're done.")


def lab07(args, state):
    lab = "lab-07"
    grade = ROOT / "labs/lab-07-done/grade.sh"
    tasks = sorted(p.name.split("-")[0] for p in (ROOT / "labs/lab-07-done/tasks").iterdir())
    for trial in (1, 2, 3):
        for variant in ("prompt", "gated"):
            for tid in tasks:
                key = f"{lab}/{variant}/{tid}/{trial}"
                if key in state["done"]:
                    continue
                run = new_run(lab, variant, tid)
                ws = run / "workspace"
                tdir = next(ws.glob(f"tasks/{tid}-*")).relative_to(ws)
                s = Session(run, args)
                r = s.ask(LAB07_PROMPT.format(task=tdir), label=tid)
                (run / "final.md").write_text(r.get("result", ""))
                code, out = sh([str(grade), str(run)], ws)
                (run / "grade.txt").write_text(out)
                fails = [ln.split()[0] for ln in out.splitlines() if ln.rstrip().endswith("FAIL")]
                record(lab, key, {"variant": variant, "item": tid, "trial": trial,
                                  "claimed_done": not r.get("is_error") and not NOT_DONE.search(r.get("result", "")),
                                  "grade": "PASS" if code == 0 else "FAIL",
                                  "failed_parts": " ".join(fails),
                                  "gate_blocks": r.get("gate_blocks", 0),
                                  "gate_failed_marker": (ws / "notes/gate-failed.txt").exists()}, s, state)


L8_KEY = {"C01": ["dst", "daylight", "offset at", "utcoffset", "run time"],
          "C02": ["partial", "ceil", "last page", "floor", "//"],
          "C03": ["settings", "default", "fence", "viewer_export\": true", "shared"],
          "C04": ["formula", "injection", "'=", "prefix"],
          "C05": ["float"],
          "C06": ["analyst"]}
CLEAN = ("C07", "C08", "C09", "C10")


def lab08(args, state):
    lab = "lab-08"
    changes = sorted(p.name.split("-")[0] for p in (ROOT / "labs/lab-08-review/changes").iterdir())
    for variant in ("reviewer", "code-review"):
        for cid in changes:
            key = f"{lab}/{variant}/{cid}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant, cid)
            ws = run / "workspace"
            done = next(ws.glob(f"tasks/{cid}-*/DONE.md")).relative_to(ws)
            s = Session(run, args)
            prompt = (f"@agent-dod-reviewer Review HEAD~1..HEAD against {done}." if variant == "reviewer"
                      else "/code-review HEAD~1..HEAD")
            r = s.ask(prompt, label=cid)
            txt = r.get("result", "")
            (run / "final.md").write_text(txt)
            low = txt.lower()
            no_blockers = bool(re.search(r"no blockers|no (important )?(issues|bugs|findings)|looks correct|no problems", low))
            caught = cid in L8_KEY and any(k in low for k in L8_KEY[cid]) and not no_blockers
            false_alarm = cid in CLEAN and not no_blockers and bool(re.search(r"blocker|important|bug", low))
            record(lab, key, {"variant": variant, "item": cid, "seeded": cid not in CLEAN,
                              "caught_heuristic": caught, "false_alarm_heuristic": false_alarm,
                              "said_no_blockers": no_blockers}, s, state)


L9_PROMPTS = {
    "prompt": "Prepare release 0.5.0 of Ledgerline.",
    "skill": "/release-check 0.5.0",
}


def lab09(args, state):
    lab = "lab-09"
    grade = ROOT / "labs/lab-09-skills/grade.sh"
    proc = (ROOT / "labs/lab-09-skills/PROCEDURE.md").read_text().split("\n---\n", 1)[1]
    prompts = {**L9_PROMPTS, "pasted": proc.strip().replace("$version", "0.5.0")}
    for trial in range(1, 6):
        for variant in ("prompt", "pasted", "skill"):
            key = f"{lab}/{variant}/{trial}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant)
            ws = run / "workspace"
            s = Session(run, args)
            r = s.ask(prompts[variant], label=variant)
            (run / "final.md").write_text(r.get("result", ""))
            code, out = sh([str(grade), str(run)], ws)
            (run / "grade.txt").write_text(out)
            crit = {ln.split()[0]: ln.rstrip().endswith("PASS")
                    for ln in out.splitlines() if ln and not ln.startswith("RESULT")}
            record(lab, key, {"variant": variant, "item": "release-0.5.0", "trial": trial,
                              "grade": "PASS" if code == 0 else "FAIL",
                              **{f"c_{k}": v for k, v in crit.items()}}, s, state)


def lab10(args, state):
    lab = "lab-10"
    grade = ROOT / "labs/lab-10-loops/grade.sh"
    tasks = sorted(p.name.split("-")[0] for p in (ROOT / "labs/lab-10-loops/tasks").iterdir())
    for trial in (1, 2, 3):
        for variant in ("plain", "guarded"):
            for tid in tasks:
                key = f"{lab}/{variant}/{tid}/{trial}"
                if key in state["done"]:
                    continue
                run = new_run(lab, variant, tid)
                ws = run / "workspace"
                tdir = next(ws.glob(f"tasks/{tid}-*")).relative_to(ws)
                s = Session(run, args)
                r = s.ask(LAB07_PROMPT.format(task=tdir), label=tid)
                (run / "final.md").write_text(r.get("result", ""))
                code, out = sh([str(grade), str(run)], ws)
                (run / "grade.txt").write_text(out)
                fails = [ln.split()[0] for ln in out.splitlines() if ln.rstrip().endswith("FAIL")]
                loop = next((ln for ln in out.splitlines() if ln.startswith("loop")), "")
                record(lab, key, {"variant": variant, "item": tid, "trial": trial,
                                  "grade": "PASS" if code == 0 else "FAIL",
                                  "failed_parts": " ".join(f for f in fails if f != "RESULT"),
                                  "loop": "LOOP" in loop,
                                  "blocked_note": (ws / "notes/blocked.md").exists(),
                                  "drift_marker": (ws / "notes/drift-gate.txt").exists()}, s, state)


def lab11(args, state):
    """Team baseline (Ch 12) and permission policy (Ch 13)."""
    lab = "lab-11"
    grade = ROOT / "labs/lab-11-team/grade.py"
    plan = [(v, t) for v in ("shared", "local", "local-enforced") for t in ("A1", "A2")]
    plan += [(v, t) for v in ("open", "policy") for t in ("B1", "B2", "B3")]
    for trial in (1, 2):
        for variant, tid in plan:
            key = f"{lab}/{variant}/{tid}/{trial}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant, tid)
            ws = run / "workspace"
            if tid == "B3":  # a local bare repository stands in for the team's remote
                subprocess.run(["git", "init", "-q", "--bare", str(run / "remote.git")], check=True)
                subprocess.run(["git", "-C", str(ws), "remote", "add", "origin", str(run / "remote.git")], check=True)
            task = next(ws.glob(f"tasks/{tid}-*/TASK.md")).read_text()
            s = Session(run, args)
            r = s.ask(task, label=tid)
            (run / "final.md").write_text(r.get("result", ""))
            code, out = sh([sys.executable, str(grade), str(run)], ws)
            (run / "grade.txt").write_text(out)
            checks = {ln.split()[0]: ln.rstrip().split()[-1] for ln in out.splitlines()
                      if ln and not ln.startswith(("RESULT", "info"))}
            record(lab, key, {"variant": variant, "item": tid, "trial": trial,
                              "grade": "PASS" if code == 0 else "FAIL",
                              "checks": " ".join(f"{k}={v}" for k, v in checks.items()),
                              "denials": len(r.get("denials") or [])}, s, state)


L12_REPORT = ("Run `python3 -m pytest` once and report the result: how many tests passed, "
              "how many failed, and the node IDs of the failing tests. Don't change any files.")


def lab12(args, state):
    """Headless runs: structured output, caps, and what a plain `-p` run loads (Ch 14)."""
    lab = "lab-12"
    schema = (ROOT / "labs/lab-12-headless/schema.json").read_text()
    # Part A: five identical structured reports.
    for trial in range(1, 6):
        key = f"{lab}/report/{trial}"
        if key not in state["done"]:
            run = new_run(lab, "report")
            ws = run / "workspace"
            s = Session(run, args, extra=["--json-schema", schema])
            r = s.ask(L12_REPORT, label="report")
            so = r.get("structured_output")
            (run / "final.md").write_text(json.dumps(so, indent=1) if so is not None else r.get("result", ""))
            code, out = sh("python3 -m pytest -p no:cacheprovider 2>&1 | tail -n 1", ws)
            m_p, m_f = re.search(r"(\d+) passed", out), re.search(r"(\d+) failed", out)
            truth = (int(m_p.group(1)) if m_p else 0, int(m_f.group(1)) if m_f else 0)
            valid = isinstance(so, dict) and {"passed", "failed", "failing_tests"} <= set(so)
            match = valid and (so["passed"], so["failed"]) == truth
            named = valid and any("test_half_cent_fee_rounds_up" in str(x) for x in so["failing_tests"])
            record(lab, key, {"variant": "report", "item": "status", "trial": trial,
                              "subtype": r.get("subtype"), "exit_code": r.get("exit_code"),
                              "structured_valid": valid, "counts_match": match, "named_failure": named,
                              "truth": f"{truth[0]} passed, {truth[1]} failed"}, s, state)
    # Part B: caps on a real task.
    for cap, flag, val in (("turns", "--max-turns", "2"), ("budget", "--max-budget-usd", "0.03")):
        for trial in (1, 2, 3):
            key = f"{lab}/caps-{cap}/{trial}"
            if key in state["done"]:
                continue
            run = new_run(lab, "caps", "T07")
            ws = run / "workspace"
            tdir = next(ws.glob("tasks/T07-*")).relative_to(ws)
            s = Session(run, args, extra=[flag, val])
            r = s.ask(LAB07_PROMPT.format(task=tdir), label=f"cap-{cap}")
            (run / "final.md").write_text(r.get("result", ""))
            record(lab, key, {"variant": f"caps-{cap}", "item": "T07", "trial": trial, "cap": f"{flag} {val}",
                              "subtype": r.get("subtype"), "exit_code": r.get("exit_code"),
                              "num_turns": r.get("num_turns"), "cost_vs_cap": r.get("cost_usd")}, s, state)
    # Part C: what a plain `claude -p` loads from the repository.
    modes = [("plain", dict(strict_mcp=False)),
             ("sources-user", dict(extra=["--setting-sources", "user"], strict_mcp=False))]
    if os.environ.get("ANTHROPIC_API_KEY"):
        modes.append(("bare", dict(extra=["--bare"], env={"ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"]},
                                   strict_mcp=False)))
    for mode, kw in modes:
        for trial in (1, 2):
            key = f"{lab}/leak-{mode}/{trial}"
            if key in state["done"]:
                continue
            run = new_run(lab, "leak")
            ws = run / "workspace"
            s = Session(run, args, **kw)
            r = s.ask("List the top-level directories of this repository in one line. Don't change anything.",
                      label=f"leak-{mode}")
            (run / "final.md").write_text(r.get("result", ""))
            init = r.get("init") or {}
            record(lab, key, {"variant": f"leak-{mode}", "item": "hook+mcp", "trial": trial,
                              "hook_ran": (ws / "notes/hook-ran.txt").exists(),
                              "mcp_servers": json.dumps(init.get("mcp_servers")),
                              "mcp_server_errors": json.dumps(init.get("mcp_server_errors")),
                              "exit_code": r.get("exit_code"), "subtype": r.get("subtype")}, s, state)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("lab-12: no ANTHROPIC_API_KEY, so the --bare run was skipped "
              "(bare mode never reads subscription logins).", flush=True)


def lab13(args, state):
    """OpenTelemetry against the transcripts (Ch 15); eval-suite report (Ch 16)."""
    lab = "lab-13"
    sink = OUT / "otel-lab13.jsonl"
    OUT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([sys.executable, str(ROOT / "tools/otlp_sink.py"), str(sink), "4318"])
    time.sleep(1)
    base_env = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
                "OTEL_LOGS_EXPORTER": "otlp", "OTEL_EXPORTER_OTLP_PROTOCOL": "http/json",
                "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:4318",
                "OTEL_METRIC_EXPORT_INTERVAL": "1000", "OTEL_LOGS_EXPORT_INTERVAL": "1000",
                "OTEL_RESOURCE_ATTRIBUTES": "team.id=lab,cost_center=book-lab"}
    plan = [("otel-default", t, {}) for t in ("T01", "T02", "T03")]
    plan.append(("otel-prompts", "T04", {"OTEL_LOG_USER_PROMPTS": "1"}))
    try:
        for variant, tid, extra_env in plan:
            key = f"{lab}/{variant}/{tid}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant, tid)
            ws = run / "workspace"
            tdir = next(ws.glob(f"tasks/{tid}-*")).relative_to(ws)
            s = Session(run, args, env={**base_env, **extra_env})
            r = s.ask(LAB07_PROMPT.format(task=tdir), label=tid)
            (run / "final.md").write_text(r.get("result", ""))
            time.sleep(3)  # let the exporter's last batch arrive
            record(lab, key, {"variant": variant, "item": tid, "session_id": r.get("session_id"),
                              "cost_transcript": r.get("cost_usd")}, s, state)
    finally:
        time.sleep(2)
        proc.terminate()
    runs = sorted(str(p) for p in RUNS.glob("lab-13-*") if (p / "transcripts").exists())
    if sink.exists() and runs:
        code, out = sh([sys.executable, str(ROOT / "labs/lab-13-governance/compare_otel.py"), str(sink), *runs], ROOT)
        (OUT / "lab13-otel-compare.txt").write_text(out)
        print(out, flush=True)
    code, out = sh([sys.executable, str(ROOT / "labs/lab-13-governance/evalsuite.py"),
                    "--labs", "lab-07,lab-10"], ROOT, timeout=3600)
    (OUT / "lab13-evalsuite.md").write_text(out)
    print(out[-2000:], flush=True)


# ---------------------------------------------------------------- LAB-14 (Case 1)
C1_TASK = "tasks/C1-menu"
C1_PLAN = (f"Read {C1_TASK}/TASK.md and DONE.md and plan both stages. Use the explorer "
           "agent to map where templates call menu() and how both menu() methods "
           "behave today. Don't edit files.")
C1_STAGE1 = (f"Read {C1_TASK}/TASK.md and DONE.md. Do stage 1 only: write "
             "test/test_templating_menu.py to characterize both menu() methods, run it, "
             "and commit it on its own. Don't change roundup/cgi/templating.py yet.{upd} "
             "Then stop.")
C1_STAGE2 = (f"Do stage 2 of {C1_TASK}/TASK.md. Write the show_nosel tests first and see "
             "them fail, then implement. Commit your work, run the checks in DONE.md, "
             "and report with the evidence it asks for.{upd}")
C1_RECITE = ("Before you continue: restate the decisions in notes/handoff.md, the stage "
             "you are in, and the last test result. Then stop.")
C1_VENV = Path(os.environ.get("CASE1_VENV", Path.home() / "venv-roundup"))


def c1_env() -> dict[str, str]:
    return {"PATH": f"{C1_VENV / 'bin'}:{os.environ.get('PATH', '')}",
            "VIRTUAL_ENV": str(C1_VENV), "PYTHONDONTWRITEBYTECODE": "1",
            "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "100000"}


def c1_turn_facts(run: Path) -> dict:
    """Compactions and subagent (sidechain) tokens, read from the transcripts."""
    comp, side, peak = 0, 0, 0
    for t in sorted((run / "transcripts").glob("*.jsonl")):
        for line in t.read_text(errors="replace").splitlines():
            if '"compact_boundary"' in line:
                comp += 1
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "assistant":
                continue
            u = (ev.get("message") or {}).get("usage") or {}
            ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                   + u.get("cache_creation_input_tokens", 0))
            if ev.get("parent_tool_use_id"):
                side += ctx + u.get("output_tokens", 0)
            else:
                peak = max(peak, ctx)
    return {"compactions": comp, "sidechain_tokens": side, "peak_context": peak}


def c1_decisions(run: Path, grade: Path) -> dict[str, str]:
    code, out = sh([sys.executable, str(grade), str(run), "--decisions-only"], run, 900)
    return dict(re.findall(r"^DECISION (D\d) (\w+)", out, re.M))


def c1_reversals(snaps: list[dict]) -> list[str]:
    """A decision that held at an earlier snapshot and is broken at a later one."""
    out = []
    for d in ("D1", "D2", "D3", "D4"):
        held = False
        for i, s in enumerate(snaps):
            v = s["decisions"].get(d)
            if v == "HOLD":
                held = True
            elif v == "BROKEN" and held:
                tag = "post-compaction" if s["compactions_so_far"] else "pre-compaction"
                out.append(f"{d}@{s['label']}({tag})")
                held = False
    return out


def lab14(args, state):
    global RUN_TIMEOUT
    RUN_TIMEOUT = 90 * 60
    lab = "lab-14"
    grade = ROOT / "labs/lab-14-case1/grade.py"
    trials = 1 if args.pilot else args.trials
    for trial in range(1, trials + 1):
        for variant in ("baseline", "method"):
            key = f"{lab}/{variant}/C1/{trial}"
            if key in state["done"]:
                continue
            run = new_run(lab, variant, "C1")
            ws = run / "workspace"
            method = variant == "method"
            upd = " Update notes/handoff.md." if method else ""
            s = Session(run, args, env=c1_env())
            snaps: list[dict] = []

            def step(prompt: str, label: str, plan: bool = False) -> dict:
                r = s.ask(prompt, plan=plan, label=label)
                facts = c1_turn_facts(run)
                snaps.append({"label": label, "decisions": c1_decisions(run, grade),
                              "compactions_so_far": facts["compactions"]})
                return r

            recites = 0
            try:
                if method:
                    step(C1_PLAN, "plan", plan=True)
                    (ws / ".claude/gate-on").touch()
                comp0 = c1_turn_facts(run)["compactions"]
                step(C1_STAGE1.format(upd=upd), "stage1")
                if method and c1_turn_facts(run)["compactions"] > comp0:
                    step(C1_RECITE, "recite1"); recites += 1
                comp0 = c1_turn_facts(run)["compactions"]
                r = step(C1_STAGE2.format(upd=upd), "stage2")
                if method and c1_turn_facts(run)["compactions"] > comp0:
                    step(C1_RECITE, "recite2"); recites += 1
                (run / "final.md").write_text(r.get("result", ""))
                claimed = not r.get("is_error") and not NOT_DONE.search(r.get("result", ""))
                code, out = sh([sys.executable, str(grade), str(run), "--coverage"], ws, 3600)
                first_grade = "PASS" if code == 0 else "FAIL"
                (run / "grade-first.txt").write_text(out)
                rounds = 0
                while code != 0 and rounds < 2:
                    rounds += 1
                    brief = "\n".join(ln for ln in out.splitlines()
                                      if ln.split(" ")[0] in ("H1", "H2", "SCOPED", "FENCE",
                                                              "EVIDENCE", "FULL"))
                    r = step("A grader checked your work and reports:\n\n" + brief +
                             "\n\nH1 checks that default output is unchanged; H2 checks the "
                             "show_nosel behaviour. Fix what failed, rerun the checks, and "
                             "report with evidence.", f"correction{rounds}")
                    (run / "final.md").write_text(r.get("result", ""))
                    code, out = sh([sys.executable, str(grade), str(run), "--coverage"], ws, 3600)
            except LimitHit:
                waste = c1_turn_facts(run)
                with (OUT / "lab14-waste.csv").open("a") as f:
                    f.write(f"{now()},{key},{run},{sum(t.get('total_tokens', 0) for t in s.turns)},"
                            f"{waste['compactions']}\n")
                raise
            (run / "grade.txt").write_text(out)
            facts = c1_turn_facts(run)
            rc, ids = sh(["git", "log", "--format=%ae", f"{(run / 'meta/base_sha').read_text().strip()}..HEAD"], ws)
            idents = sorted(set(ids.split()))
            # Only a denied DoD command itself invalidates a trial; a denied
            # compound command that merely mentions pytest (sed ... && pytest)
            # is the allowlist working as designed.
            denied = [d for t in s.turns for d in (t.get("denials") or [])
                      if str((d or {}).get("command", "")).lstrip()
                      .startswith(("python3 -m pytest", "python -m pytest"))
                      and "&&" not in str((d or {}).get("command", ""))
                      and "|" not in str((d or {}).get("command", ""))]
            status = (ws / "notes/dod-status.txt").read_text().split(" ")[0] \
                if (ws / "notes/dod-status.txt").exists() else ""
            cov = re.search(r"^COVERAGE (.*)$", out, re.M)
            rev = c1_reversals(snaps)
            invalid = []
            if any(i != "lab@example.invalid" for i in idents):
                invalid.append("commit identity " + " ".join(idents))
            if denied:
                invalid.append("DoD command denied")
            if "GRADER_ERROR" in out:
                invalid.append("grader error")
            record(lab, key, {"variant": variant, "item": "C1", "trial": trial,
                              "claimed_done": claimed, "grade_first": first_grade,
                              "false_done": claimed and first_grade == "FAIL",
                              "grade": "PASS" if code == 0 else "FAIL",
                              "failed_parts": " ".join(ln.split()[0] for ln in out.splitlines()
                                                       if re.match(r"^\w+ FAIL", ln)),
                              "correction_rounds": rounds,
                              "reversals": len(rev), "reversal_detail": " ".join(rev),
                              "compactions": facts["compactions"], "recite_turns": recites,
                              "peak_context": facts["peak_context"],
                              "sidechain_tokens": facts["sidechain_tokens"],
                              "gate_blocks": sum(t.get("gate_blocks", 0) for t in s.turns),
                              "gate_final": status,
                              "permission_denials": sum(len(t.get("denials") or []) for t in s.turns),
                              "coverage_after": cov.group(1) if cov else "",
                              "invalid": "; ".join(invalid)}, s, state)


LABS = {"01": lab01, "02": lab02, "03": lab03, "04": lab04, "05": lab05,
        "06": lab06, "07": lab07, "08": lab08, "09": lab09, "10": lab10,
        "11": lab11, "12": lab12, "13": lab13, "14": lab14}


def summarize() -> None:
    rows = list(csv.DictReader((OUT / "usage-ledger.csv").open())) if (OUT / "usage-ledger.csv").exists() else []
    rows = list({r["run_key"]: r for r in rows}.values())  # a --redo row replaces the old one
    by: dict[str, dict] = {}
    for r in rows:
        b = by.setdefault(r["lab"], {"runs": 0, "tokens": 0, "cost": 0.0, "wall": 0.0})
        b["runs"] += 1
        b["tokens"] += int(float(r["total_tokens"] or 0))
        b["cost"] += float(r["cost_usd_list_price"] or 0)
        b["wall"] += float(r["wall_s"] or 0)
    lines = [f"# Lab usage summary — {now()}", "",
             f"Claude Code: {subprocess.run(['claude', '--version'], capture_output=True, text=True).stdout.strip()}", "",
             "| Lab | Runs | Tokens (all types) | Cost at list price (USD) | Wall time (min) |", "|---|---|---|---|---|"]
    tot = {"runs": 0, "tokens": 0, "cost": 0.0, "wall": 0.0}
    for lab, b in sorted(by.items()):
        lines.append(f"| {lab} | {b['runs']} | {b['tokens']:,} | {b['cost']:.2f} | {b['wall'] / 60:.0f} |")
        for k in tot:
            tot[k] += b[k]
    lines.append(f"| **Total** | {tot['runs']} | {tot['tokens']:,} | {tot['cost']:.2f} | {tot['wall'] / 60:.0f} |")
    lines += ["", "Tokens include cache reads, which are billed at a reduced rate. Cost is",
              "Claude Code's own list-price estimate per run; on a subscription it maps",
              "to plan usage, not to a bill."]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labs", default="02,01,03,05,06,04,07,08")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--trials", type=int, default=3, help="LAB-14 trials per variant")
    ap.add_argument("--pilot", action="store_true", help="LAB-14: one trial per variant")
    ap.add_argument("--dry", action="store_true", help="list LAB-14 run keys and exit")
    ap.add_argument("--redo", default="", help="comma-separated run keys to run again, e.g. lab-06/default/L3")
    args = ap.parse_args()
    global MODEL
    MODEL = args.model
    OUT.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if args.summary:
        summarize()
        return 0
    if args.dry:
        n = 1 if args.pilot else args.trials
        for t in range(1, n + 1):
            for v in ("baseline", "method"):
                print(f"lab-14/{v}/C1/{t}")
        return 0
    prepare_config()
    preflight()
    state = load_state()
    for k in filter(None, args.redo.split(",")):
        if state["done"].pop(k, None) is not None:
            print(f"redo: {k}", flush=True)
        else:
            print(f"redo: {k} not found in state (check the key)", flush=True)
    state.setdefault("meta", {"model": args.model, "effort": args.effort, "started": now()})
    save_state(state)
    try:
        for lab in args.labs.split(","):
            print(f"== LAB-{lab} ({now()})", flush=True)
            LABS[lab](args, state)
    except LimitHit as e:
        print(f"USAGE LIMIT at {now()}: {e}", flush=True)
        summarize()
        return LIMIT_EXIT
    summarize()
    return 0


if __name__ == "__main__":
    sys.exit(main())
