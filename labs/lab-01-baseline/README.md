# LAB-01 — Baseline day (Chapter 1)

**Measures:** session-start context, per-task tokens and time, pass/rework,
seven-day attribution, cache hit rate.
**Time:** about 60 minutes over one working day.

## Setup
1. Install the status line: copy `templates/statusline/statusline-full.sh` to
   `~/.claude/statusline.sh`, make it executable, and merge
   `templates/settings/statusline.json` into `~/.claude/settings.json`.
2. Fill in the header of `baseline-sheet.md`: Claude Code version, plan, model,
   effort.

## Protocol
1. `tools/new-run.sh lab-01 base` and start `claude` in the workspace.
   Before typing anything, run `/context`. Record the total and top three
   categories. Exit.
2. For each task A, B, C in `tasks/`: new run, fresh session, paste the TASK.md
   text. At the end record end context % (status line), tokens and cost from
   `/usage`, wall-clock minutes, pass or rework.
3. At the end of the day: `/usage`, press `w` for 7 days; record the top three
   consumers and any behavior flags. Record the `Prompt cache (main)` line.

## Pass criteria
- A: `python3 -m pytest tests/acceptance/test_a_roles.py` and `make test lint typecheck` pass.
- B: the review states whether the overdue check is correct, with a reason.
- C: mentions grace period, proration, minimum fee, float rounding risk.
