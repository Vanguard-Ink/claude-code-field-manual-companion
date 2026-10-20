# Done — Viewer export behind a flag

## Requirements
- Viewers may export only when the `viewer_export` flag is on.
- Default settings are unchanged: no flags on.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
- packages/shared/ (no changes in this task)
