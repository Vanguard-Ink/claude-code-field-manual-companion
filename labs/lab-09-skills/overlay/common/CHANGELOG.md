# Changelog

All notable changes to Ledgerline. Format: Keep a Changelog.

## [Unreleased]

### Added
- CSV export for reports.
- `LEDGERLINE_DEFAULT_TIMEZONE` overrides the default time zone.

### Fixed
- Gateway timeouts during a charge are retried.
- The web handler returns 404 for an unknown report.

## [0.4.2] - 2026-09-14

### Fixed
- Invoice numbers are zero-padded to six digits.

## [0.4.1] - 2026-08-30

### Fixed
- Late fees no longer round in float.
