# Done — Page count for report listings

## Requirements
- `ReportService.page_count(per_page)` returns how many pages `list_reports` produces.
- per_page below 1 is an error.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
