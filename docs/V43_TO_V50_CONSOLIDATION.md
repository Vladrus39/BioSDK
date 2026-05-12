# v4.3 to v5.0 Consolidation

## Decision

`biogpu-core-v5_0_bic_os_first_mover_roadmap` is the canonical working project.

`biogpu-core-v4_3_hosted_server_scaffold` is no longer needed as a separate active workspace after this consolidation, because all unique non-cache v4.3 files have been copied into the v5.0 legacy archive.

## What was copied

Unique v4.3 files that were not already present in v5.0 at the same relative path or under `evidence/` were copied to:

`legacy/v4_3_unique_archive/`

Copied file groups:

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

Total copied: 181 source files.

## Integrity

The archive includes:

- `legacy/v4_3_unique_archive/MANIFEST_V43_UNIQUE_FILES.csv` — SHA256 manifest for copied files.
- `legacy/v4_3_unique_archive/README_V43_UNIQUE_ARCHIVE.md` — archive policy and counts.

## Active development rule

Do not develop in v4.3 anymore. Use v5.0 as the single source of truth.

Historical tests under `legacy/v4_3_unique_archive/tests/` are reference-only and must not be added to active pytest collection. Current release tests remain under `tests/current/`.

## Safe deletion

After confirming the v5.0 validation checks pass, the standalone `biogpu-core-v4_3_hosted_server_scaffold` folder can be deleted by the user.
