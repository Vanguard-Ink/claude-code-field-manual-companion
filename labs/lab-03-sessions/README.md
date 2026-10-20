# LAB-03 — One long session vs three cleared sessions (Chapter 3)

**Measures:** total tokens, context at the end of each task, wall time, pass/rework.
**Tasks:** A, B, C from LAB-01 (same text, in `tasks/`).
**Time:** about 60 minutes.

## Protocol
- **Run A (long):** `tools/new-run.sh lab-03 long`. One session: task A, then B,
  then C, no `/clear`. After each task record the context % and cumulative
  `/usage` session tokens.
- **Run B (cleared):** `tools/new-run.sh lab-03 cleared`. Task A, record,
  `/rename lab03-a`, `/clear`; repeat for B and C.
- Choose model and effort before the first prompt and don't change them.
