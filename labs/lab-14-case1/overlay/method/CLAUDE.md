# Roundup (pinned for LAB-14)

Issue tracker in Python. The code under change is `roundup/cgi/templating.py`.

- Tests: `python3 -m pytest -p no:cacheprovider <files>`. The full suite takes
  minutes; run the files named in the task's DONE.md.
- `roundup/cgi/TAL/`, `PageTemplates/`, `ZTUtils/` and `roundup/anypy/vendored/`
  are vendored. Don't read or change them.
- Test fixtures: `roundup.test.memorydb` gives an in-memory tracker (see the
  setUp of `HTMLPropertyTestClass` in `test/test_templating.py`).
- Keep the task's decisions in `notes/handoff.md`, and update it after each
  stage.

# Compact instructions

Keep: the task's decisions D1-D4, the stage you are in, the files you changed,
the exact test command and its last result, and open questions. Drop: file
listings and test output that passed.
