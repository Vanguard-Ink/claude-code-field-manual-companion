# C1: menu() can hide "- no selection -" (issue 2551121)

Roundup's `roundup/cgi/templating.py` renders `<select>` menus for Link and
Multilink properties with `LinkHTMLProperty.menu()` and
`MultilinkHTMLProperty.menu()`. Both always add a "- no selection -" option.
Issue 2551121 asks for a way to hide it, so users are gently forced to choose.

Work in two stages, in the order given by the prompts.

## Stage 1: characterize

Write `test/test_templating_menu.py`. It records what both `menu()` methods
render today for representative inputs, and asserts against that recording.
Don't change `templating.py` in this stage. Commit the new test file on its own.

## Stage 2: change

- Add a keyword argument `show_nosel=True` to both `menu()` methods, before
  `**conditions`.
- When it is False, leave the "- no selection -" option out. In the
  Multilink menu it then no longer counts toward the computed height.
- Document the argument in both docstrings and add one line to `CHANGES.txt`.
- Add tests for the new argument to `test/test_templating_menu.py`, and see
  them fail before you implement.

## Decisions (do not reverse)

- D1: the default output of both methods stays byte-identical.
- D2: the argument is named `show_nosel`, defaults to True, and is on both
  methods.
- D3: new tests go in `test/test_templating_menu.py` only.
- D4: no edits under `share/`.
