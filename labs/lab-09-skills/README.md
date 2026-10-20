# LAB-09 — Prompt vs pasted procedure vs skill (Chapter 10)

**Question:** does encoding a procedure as a skill make it run the same way
every time, and is the gain from the skill mechanism or just from writing the
procedure down?

**Task:** prepare release 0.5.0 of Ledgerline: run the three checks, bump the
version in two files, roll the changelog, write release notes, and do *not*
tag, push, or commit.

**Variants (k = 5 runs each, fresh workspace per run):**

| Variant | What you send |
|---|---|
| `prompt` | `Prepare release 0.5.0 of Ledgerline.` |
| `pasted` | The text of `PROCEDURE.md` below the line, with `$version` = 0.5.0 |
| `skill` | `/release-check 0.5.0` (skill in `overlay/skill/.claude/skills/`) |

The `prompt` variant can't know the team's notes format, so it is expected to
fail the `notes` criterion. It is there to show what a one-line request leaves
out. The comparison that matters is `pasted` vs `skill`: same steps, different
mechanism.

## Protocol
1. `tools/new-run.sh lab-09 <variant>`; start `claude` in the workspace.
2. Send the variant's message. Don't help.
3. Save the final message to `<run>/final.md`.
4. `labs/lab-09-skills/grade.sh <run> > <run>/grade.txt`
5. After all 15 runs: `python3 labs/lab-09-skills/summarize.py`.
   Record pass^5 per variant, the per-criterion counts, and tokens per run
   (status line or `/cost`) in `results/record.csv`.

## Criteria (grade.sh)
`version` both files · `changelog` entries moved verbatim, dated, history
intact · `notes` headings and exit codes · `effects` no tag, no commit ·
`scope` only the four release files · `regress` checks still green.
