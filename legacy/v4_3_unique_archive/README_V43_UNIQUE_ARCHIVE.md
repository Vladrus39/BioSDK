# v4.3 Unique Archive

This folder contains the v4.3 files that were not already present in v5.0 either at the same relative path or under `evidence/`.

Purpose: preserve v4.3-only documentation, scripts, historical tests, hardware notes, research notes and benchmark registry assets before deleting the standalone `biogpu-core-v4_3_hosted_server_scaffold` workspace folder.

## Source

- Source folder: `biogpu-core-v4_3_hosted_server_scaffold`
- Target folder: `legacy/v4_3_unique_archive`
- Unique source files copied: 181
- Integrity manifest: `MANIFEST_V43_UNIQUE_FILES.csv`

## Counts by original top-level path

| Count | Original path |
| ---: | --- |
| 68 | `docs/` |
| 50 | `scripts/` |
| 47 | `tests/` |
| 6 | `hardware/` |
| 4 | `research/` |
| 3 | `benchmarks/` |
| 1 | `__init__.py` |
| 1 | `README_BIOGPU_CORE_V40_BETA.md` |
| 1 | `README_BIOGPU_CORE.md` |

## Use policy

These files are archived for reference and recovery. Do not add `legacy/v4_3_unique_archive/tests` to active pytest collection. Current release tests remain under `tests/current`.
