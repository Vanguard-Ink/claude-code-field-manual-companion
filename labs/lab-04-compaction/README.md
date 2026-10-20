# LAB-04 — Context through compaction (Chapter 4)

**Task:** `tasks/R01-retry-refactor` — six steps, two decisions that later steps
tempt you to reverse (keep `retry_helper.py` deleted; keep `charge()`'s signature).
**Variants:** `default` (no handoff, no hook) and `designed` (handoff file,
`compact` SessionStart hook, `# Compact instructions` in CLAUDE.md).
**Time:** about 90 minutes for both runs; 45 more for the optional restart run.

## Protocol (same for both variants)
1. `tools/new-run.sh lab-04 <variant> R01`, start `claude`.
2. Designed only: press Shift+Tab into plan mode and ask for a six-step plan;
   approve it.
3. Paste: "Do the task in tasks/R01-retry-refactor/TASK.md, one step at a time."
4. **Compaction is forced, not left to chance:** after step 2 and after step 4,
   run `/compact` (no instructions). In the designed run, then send the recite
   prompt from Chapter 4 before continuing.
5. When Claude says it's done, save the final message to `<run>/final.md` and run
   `./grade.sh <run>`. Record grade, `REVERSED_DECISIONS`, and how many times you
   had to correct Claude.

**Run C (optional):** designed setup, but after step 2 use `/clear` and start a
fresh session that reads `notes/handoff.md`, instead of `/compact`.
