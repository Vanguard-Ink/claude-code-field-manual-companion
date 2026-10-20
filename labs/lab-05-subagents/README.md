# LAB-05 — Exploration in the main session vs a subagent (Chapter 5)

**Questions:** `questions.md` (five "where is X decided" questions + one
unrelated follow-up). **Answer key:** `key/answers.md` — don't open it in a session.
**Variants:** `main` and `delegated` (both include `.claude/agents/code-locator.md`;
only `delegated` uses it; the runner denies `Agent(code-locator)` in `main`).
**Time:** about 45 minutes.

## Protocol
1. `tools/new-run.sh lab-05 main`, one session, ask questions 1–6 in order.
   After each answer record the context %.
2. `tools/new-run.sh lab-05 delegated`, same, but prefix 1–5 with
   `@agent-code-locator`.
3. Score answers 1–5 with the rubric in `key/answers.md`. Record total tokens
   per run and the cost of question 6 alone.
