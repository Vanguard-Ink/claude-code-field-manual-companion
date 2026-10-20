# Done — <task title>

## Target (must go fail → pass)
- tests/acceptance/<test file>
  (written and committed before the change)

## No regressions (must stay pass → pass)
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- <public interfaces that must keep their shape>
- tests/acceptance/ except this task's new file
- migrations/, .github/

## Evidence in the final message
- Each command above and its last 20 lines
- `git diff --stat`

## Running app
- /verify: <what a user would do to see it work>
