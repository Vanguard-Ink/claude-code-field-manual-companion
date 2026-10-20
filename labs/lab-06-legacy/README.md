# LAB-06 — Legacy setup (Chapter 6; feeds Case 1)

**Tasks:** L1 locate a rounding bug, L2 trace a cross-package call path, L3 fix
the bug with characterization tests first.
**Variants:** `default` (start at the root, no package CLAUDE.md, no deny rules)
and `scoped` (package CLAUDE.md files, `Read` deny rules for generated and
vendored code, `claudeMdExcludes` for `packages/legacy-*`; start in
`packages/billing` with `../shared` as an additional directory). Install a
Python code-intelligence plugin for the scoped run if one is available to you.
**Time:** about 90 minutes.

## Protocol
1. For each task and variant: `tools/new-run.sh lab-06 <variant> L1|L2|L3`.
   Default: start `claude` in `workspace/`. Scoped: start it in
   `workspace/packages/billing/`.
2. Before the first prompt, `/context`: record the session-start total.
3. Paste the task's TASK.md. Count files read (from the transcript).
4. L1/L2: score with `DONE.md` (one point per line). L3: `./grade.sh <run>`.
5. Record line coverage of `fees.py` before (0%) and after characterization.
