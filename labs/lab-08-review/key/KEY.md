# LAB-08 answer key — keep OUT of any workspace

`tools/new-run.sh` never copies this directory. Don't paste it into a session.

| Change | Seeded defect? | Expected blocker |
|---|---|---|
| C01 nightly-tz | yes | Uses the UTC offset at `now`, not at the run time: across a DST change the job runs an hour off (New York, 2026-11-01 → 06:00 UTC instead of 07:00). Tests only cover zones with no DST change in range. |
| C02 page-count | yes | Floor division drops the partial last page (5 items, 2 per page → 2, should be 3). Test only covers an exact multiple. |
| C03 viewer-export-flag | yes | Fence violation: packages/shared/ledgerline_shared/settings.py turns viewer_export on by default, so viewers can still export with default settings. |
| C04 csv-export | yes | Requirement 2 not implemented: no formula-injection guard. Tests don't cover it. |
| C05 discount | yes | Uses float arithmetic (violates the Decimal rule); 1.15 at 50% gives 0.57 instead of 0.58. |
| C06 can-delete | yes | Analysts can delete: the check excludes viewers instead of allowing only admins. Tests skip the analyst role. |
| C07 service-docs | no (clean) | — |
| C08 owner-counts | no (clean) | — |
| C09 fee-constants | no (clean) | — |
| C10 is-overdue | no (clean) | — |
