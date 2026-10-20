# LAB-12 — Headless runs: reproducible, capped, isolated (Chapter 14)

**Measures:**
- **Part A, reproducibility.** Five identical `claude -p --json-schema` runs that report the test suite's status as JSON. For each run, the grader records whether `structured_output` was present and valid, whether the counts match what the grader's own `pytest` run reports, and the run's tokens, cost and time.
- **Part B, caps.** The same task (T07, money rounding) runs three times under `--max-turns 2` and three times under `--max-budget-usd 0.03`. For each run, the grader records the result `subtype`, the exit code, and the actual cost against the cap.
- **Part C, what a plain `-p` run loads.** The workspace commits a SessionStart hook that writes `notes/hook-ran.txt`, standing in for a teammate's hook. It also commits a `.mcp.json` that points at a server that doesn't exist. The grader records three things: whether the hook ran, the `system/init` event's `mcp_servers` (each server's `status`: a server whose command doesn't exist shows as `failed`) and `mcp_server_errors` (which lists only `--mcp-config` entries that fail validation, so it stays empty here), and the exit code. Neither mode passes `--strict-mcp-config`, so the `.mcp.json` result reflects the mode itself. There are two modes. `plain` is `claude -p` with nothing extra. `sources-user` adds `--setting-sources user`, so the project's settings and hooks are skipped. When `ANTHROPIC_API_KEY` is set, a third mode, `bare`, adds `--bare`. Bare mode never reads subscription (OAuth) logins, so on a Pro or Max login without an API key, the runner skips the `bare` mode.

**Variants:**
- `report`: adds one failing acceptance test, so the honest answer is "1 failed".
- `caps`: T07 task material.
- `leak`: the hook and the broken `.mcp.json`.

**Run with the runner:**

```bash
python3 tools/run-labs.py --labs 12
```

The runner adds the extra flags itself: `--json-schema` (from `schema.json`), `--max-turns`, `--max-budget-usd`, and `--bare`. Permissions are the same as in every other lab: `dontAsk` plus the exact-command allowlist. No run uses `--dangerously-skip-permissions`.

**Time:** about 20 minutes, 15 sessions (17 with an API key).

**By hand:** run the same commands from `tools/run-labs.py` (`lab12`) in a workspace created by `tools/new-run.sh lab-12 <variant> [item]`.
