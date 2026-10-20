# LAB-10 — Loops, bloat, and duplicates (Chapter 11)

**Question:** how often do loops, unrequested code, and duplicate helpers
show up, and do Chapter 11's guards catch them?

## Part A — retro scan (no tokens)
After LAB-07 has run, scan what its 60 runs left behind:

    python3 labs/lab-10-loops/retro.py lab-07

It runs `loopscan.py` on each transcript (same command failing the same way
three times in a row = loop) and `templates/hooks/dupcheck.py` on each
workspace. Record the totals per variant.

## Part B — trap tasks, guards off vs on
Four tasks, each built to invite one failure:

| Task | Invites | Correct outcome |
|---|---|---|
| X1 statement total | re-implementing cents rounding | reuse `to_cents` |
| X2 refund retry | a hand-rolled retry loop | reuse `with_retries` |
| X3 nightly hour from env | a config framework | ~8 lines in `settings.py` |
| X4 volume discount | a loop: the tests contradict each other | stop, write `notes/blocked.md` |

Variants: `plain` (sample-app as is) and `guarded`: the CLAUDE.md
"before you write new code" rules, `loop-guard.sh` on PostToolUseFailure,
and `drift-gate.sh` (dupcheck + Scope) on Stop
(`templates/settings/loop-guards.json`). Both variants get the same
DONE.md, including its Scope list and "If you can't finish" section.

k = 3 per task and variant: 24 runs.

1. `tools/new-run.sh lab-10 <plain|guarded> X0N`; start `claude`.
2. Paste: "Do the task in tasks/X0N-*/TASK.md. Run the checks in its
   DONE.md and show their output before you say you're done."
3. Don't help. Save the final message to `<run>/final.md`. If you ran it
   by hand, copy the session transcript (`~/.claude/projects/...jsonl`)
   to `<run>/transcripts/`.
4. `labs/lab-10-loops/grade.sh <run> > <run>/grade.txt`
5. `python3 labs/lab-10-loops/summarize.py`

`grade.sh` criteria: outcome (`target`, or `outcome` for X4), `regress`,
`fence`, `dup`, `scope`, `public` (no unrequested public names), `size`
(over 3x the reference's added lines and 15+ lines more = bloat), and
`loop` (from the transcript; reported, not graded).
