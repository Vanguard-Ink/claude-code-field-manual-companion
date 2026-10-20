# Release procedure (pasted variant)

The runner pastes everything below the line, with
`$version` replaced by the target version.

---

Prepare release $version.

Find today's date (UTC) with `date -u +%F` and the
current version in `VERSION`.

Do these steps in order. Stop at the first failure.

1. Run `make test`, `make lint`, and
   `make typecheck` one at a time. Note each exit
   code. If any is not 0, stop and report; change
   nothing.
2. Set the version to $version in `VERSION` and in
   `packages/shared/ledgerline_shared/version.py`.
3. In `CHANGELOG.md`, rename `## [Unreleased]` to
   `## [$version] - <today>` and add an empty
   `## [Unreleased]` above it. Move the entries;
   don't reword them. Leave older sections as is.
4. Write `release/$version.md` with exactly these
   headings: `# Release $version`, `## Checks`
   (each command and its exit code), `## Changes`
   (the entries from step 3), `## Not done`.
5. Under "Not done", list: tag, push, publish.
   Never do these yourself, and don't commit.

Change only `VERSION`, `version.py`, `CHANGELOG.md`,
and the new notes file. Reply with the notes path
and the three exit codes.
