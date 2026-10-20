# roundup/cgi

- `templating.py` is 4,000 lines. Find code with Grep and read the ranges you
  need, not the whole file.
- `LinkHTMLProperty.menu` and `MultilinkHTMLProperty.menu` render the
  `<select>` menus. Templates under `share/` call them; their default output
  must not change.
