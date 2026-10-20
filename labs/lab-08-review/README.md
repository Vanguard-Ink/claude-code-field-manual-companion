# LAB-08 — Does the reviewer earn its cost? (Chapter 9)

**Changes:** `changes/C01`–`C10`. Every change passes `make check`. Six carry a
seeded defect the tests miss; four are clean. **Answer key and oracle tests:**
`key/` — never copied into a workspace; don't open it in a session.
**Variants:** `none` (no review), `reviewer` (the `dod-reviewer` subagent),
`code-review` (`/code-review` at default effort).
**Time:** about 2 hours.

## Protocol
1. `tools/new-run.sh lab-08 <variant> C0N`. The workspace has two commits:
   the base, and the change under review. The change's DONE.md is in `tasks/`.
2. `reviewer`: copy `templates/agents/dod-reviewer.md` into the workspace's
   `.claude/agents/` first, then:
   `@agent-dod-reviewer Review HEAD~1..HEAD against tasks/C0N-*/DONE.md.`
   `code-review`: run `/code-review HEAD~1..HEAD`.
3. Record every finding and its severity. Then compare with `key/KEY.md`:
   a blocker that matches the seeded defect is a catch; a blocker on a clean
   change is a false alarm.
4. To confirm a defect independently: copy `key/oracles/test_oracle_c0N.py` into
   the workspace's `tests/` and run it (fails = defect present).
