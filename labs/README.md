# Labs

| Lab | Chapter | Folder | Grader |
|---|---|---|---|
| LAB-01 Baseline day | 1 | lab-01-baseline | manual (baseline sheet) |
| LAB-02 Session-start budget | 2 | lab-02-session-start | `check-probe.sh` |
| LAB-03 Long vs cleared sessions | 3 | lab-03-sessions | manual + task A test |
| LAB-04 Context through compaction | 4 | lab-04-compaction | `grade.sh` |
| LAB-05 Exploration: main vs subagent | 5 | lab-05-subagents | rubric (`key/`) |
| LAB-06 Legacy setup | 6, 17 | lab-06-legacy | `grade.sh` (L3) + rubric (L1, L2) |
| LAB-07 False done: prompt vs gates | 7, 8 | lab-07-done | `grade.sh`, `summarize.py` |
| LAB-08 Reviewer value | 9 | lab-08-review | `key/` oracles |
| LAB-09 Prompt vs pasted vs skill | 10 | lab-09-skills | `grade.sh`, `summarize.py` |
| LAB-10 Loops, bloat, duplicates | 11 | lab-10-loops | `retro.py` (A), `grade.sh`, `summarize.py` (B) |
| LAB-11 Team baseline and policy | 12, 13 | lab-11-team | `grade.py` |
| LAB-12 Headless: structure, caps, isolation | 14 | lab-12-headless | in `tools/run-labs.py` (`lab12`) |
| LAB-13 Telemetry and the team eval suite | 15, 16 | lab-13-governance | `compare_otel.py`, `evalsuite.py` |
| LAB-14 Case 1: Roundup `menu()` (issue 2551121) | 17 | lab-14-case1 | `grade.py` (hidden `key/`), `validate-key.sh` |

## Every run

1. Activate the venv you created in the top-level README.
2. `tools/new-run.sh <lab> <variant> [item]` — prints the run folder.
3. `cd` into `<run>/workspace` and start `claude` there (fresh session).
4. Follow the lab's README. Save Claude's final message to `<run>/final.md`.
5. Run the lab's grader if it has one, and add a row to `results/record.csv`.

Runs go to `~/ccfm-runs` unless you set `CCFM_RUNS`.
