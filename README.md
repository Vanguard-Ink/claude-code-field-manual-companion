# Claude Code Field Manual — companion repository

Templates, a sample service, and runnable labs for *Claude Code Field Manual*
by Nathan Tran.

Home: https://github.com/Vanguard-Ink/claude-code-field-manual-companion.
Use the release tagged for your edition (`v1.0` = first edition, 2026) so the
files match the printed pages. Corrections: [ERRATA.md](ERRATA.md); report a
problem through Issues.

This is an independent guide. It is not affiliated with, endorsed by, or
sponsored by Anthropic. Claude and Claude Code are trademarks of Anthropic, PBC.

## What's here

| Path | What |
|---|---|
| `templates/` | Every config file printed in the book: status lines, hooks (gates, loop guard, drift gate), settings, subagents, DONE.md, handoff file, canonical helpers list |
| `sample-app/` | **Ledgerline**, a small fictional Python service the labs run against |
| `labs/` | One folder per lab: protocol (`README.md`), assets, graders, record sheets |
| `tools/new-run.sh` | Creates an isolated, git-initialised copy of the sample app for one lab run |
| `tools/selftest.sh` | Checks every template, grader, and reference solution without calling Claude |
| `tools/run-labs.py` | Runs labs headless (`claude -p`, scoped permissions) and records tokens per run |

## Quick start

```bash
python3 -m venv ~/.venvs/ccfm && . ~/.venvs/ccfm/bin/activate
pip install -r sample-app/requirements-dev.txt
tools/selftest.sh            # everything should print PASS
tools/new-run.sh lab-07 prompt T01
```

Requirements: Python 3.11+, git, make, bash, jq. On Windows, use Git Bash or WSL.

## Ground rules for the labs

- One run = one fresh copy of the sample app (`tools/new-run.sh`). Never reuse a
  workspace between runs.
- Graders, answer keys, and reference solutions stay in this repository. They are
  never copied into a workspace, so the agent can't read or edit them.
- Record the Claude Code version, plan, model, and effort for every run. Numbers
  from different setups aren't comparable.
- Measured results go in `labs/<lab>/results/`. The book prints only numbers
  that came from these runs.

License: MIT (see `LICENSE`).
