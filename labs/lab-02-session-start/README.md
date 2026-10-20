# LAB-02 — Session-start budget, before and after (Chapter 2)

**Measures:** session-start tokens and the five rule probes, before vs after a trim.
**Variants:** `before` (300-line CLAUDE.md, 3 unscoped rules, 8 skills with long
descriptions, 2 MCP servers) and `after` (the trimmed setup).
**Time:** about 75 minutes.

## Protocol
1. `tools/new-run.sh lab-02 before`. Fresh session, no prompt, `/context`.
   Record total and top categories.
2. For each probe in `probes.md`: a new `before` run, fresh session, paste the
   probe, let Claude finish, then `./check-probe.sh <run> P1` (etc.).
3. Repeat steps 1–2 with `after`.
4. Optional: do the trim yourself on a `before` run, following Chapter 2's six
   steps, and compare your result with `overlay/after/`.

The MCP servers in `before` start with `npx`; you need Node.js for them to load.
