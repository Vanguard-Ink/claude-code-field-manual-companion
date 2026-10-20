# Done: C1 menu() show_nosel

## Target (fail, then pass)
- the `show_nosel` tests in `test/test_templating_menu.py`, written before
  the change

## No regressions (pass, then pass)
- `python3 -m pytest -p no:cacheprovider test/test_templating.py test/test_cgi.py test/test_templating_menu.py`
  exits 0

## Fence (must not change)
- `test/` except `test/test_templating_menu.py`
- `share/`
- `roundup/` except `roundup/cgi/templating.py`
- `pyproject.toml`, `.github/`

## Evidence in the final message
- the command above and the last 20 lines of its output
- `git diff --stat` against the starting commit
- `git log --oneline -3`

## If you can't finish
Write `notes/blocked.md`: what you tried, the failing output, two hypotheses.
Then stop and say it isn't done.
