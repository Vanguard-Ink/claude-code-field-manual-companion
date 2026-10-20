# LAB-14: Case 1 on Roundup (Chapter 17)

One real legacy codebase, one real change: issue 2551121 in Roundup's
`roundup/cgi/templating.py` (pinned at git 393187a, hg rev 8831). Two
variants, same task, same grader:

| | `baseline` | `method` |
|---|---|---|
| Start | upstream repo, no CLAUDE.md | lean CLAUDE.md + `roundup/cgi/CLAUDE.md`, deny rules |
| Plan | none | plan-mode turn with the read-only `explorer` subagent |
| Handoff | none | `notes/handoff.md`, reloaded by a SessionStart `compact` hook; a recite turn after a turn that compacted |
| Gate | none | Stop gate v2 (`dod-gate-case1.sh`), on after the plan turn |
| Agent tool | denied | allowed |

Both variants: `CLAUDE_CODE_AUTO_COMPACT_WINDOW=100000`, `dontAsk` with the
runner's allowlist, Sonnet 5.5 at medium effort, no bypass mode.

Conclusions are at the level of the whole bundle: the lab doesn't separate
the effect of the handoff, the gate, the explorer, or the plan.

## Setup (once, about 15 minutes)

    labs/lab-14-case1/setup-roundup.sh

Clones Roundup at the pinned commit into `$CCFM_RUNS/_cache/`, builds
`~/venv-roundup`, validates the grader (untouched tree passes H1 and fails
H2; the reference passes everything; each of 5 mutants fails), and records
the baseline: scoped-suite time, two full-suite runs, failures present in
either baseline run (ignored by the grader), and `menu()` coverage before.

## Run

    python3 tools/run-labs.py --labs 14 --pilot     # 2 trials
    python3 tools/run-labs.py --labs 14             # main: 3 per variant

`--dry` lists the run keys. A usage limit stops the runner with exit 75;
the interrupted trial is thrown away and starts clean on the next run
(its tokens go to `_results/lab14-waste.csv`).

## Grader (`grade.py`, hidden)

Copies the workspace to `<run>/grade-ws` and checks there:
- **H1** default output of both `menu()` methods equals goldens (32 cases)
- **H2** `show_nosel=False` omits the option (and the Multilink height
  drops by one); `True` equals the default; the argument never reaches
  `filter()` as a condition
- **SCOPED** the DoD regression command; **FULL** the whole suite, minus
  baseline failures; **FENCE**; **EVIDENCE** in the final message
- **DECISION D1-D4** after every turn, for the reversal count

## Pilot gate (before the main run)

Both pilot trials valid (`invalid` column empty), grader matches a hand
check of the diff, at least one compaction per variant, and tokens within
the spec's estimate (pilot 6.5-13M). Otherwise stop and re-plan.
