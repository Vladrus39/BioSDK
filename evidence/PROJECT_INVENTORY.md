# Project inventory — biogpu-core v0.8

## Core package

- `biogpu/cli.py` — CLI entry point.
- `biogpu/api/server.py` — FastAPI app.
- `biogpu/substrates/` — SimulatedMEA, RealMEA dry-run, MaxOne-like dry-run.
- `biogpu/benchmarks/` — synthetic and real-data benchmarks.
- `biogpu/data_ingest/` — public-data adapters and stimulus-window mapping.
- `biogpu/data/` — logging, HDF5/NWB-like export, energy, versioning, plots.
- `biogpu/diagnostics/` — regression diagnostics and repeated-seed utilities.
- `biogpu/dashboard/` — static dashboard generation.

## New v0.8 files

- `biogpu/data_ingest/stimulus_windows.py`
- `biogpu/data_ingest/dandi_discovery.py`
- `biogpu/data_ingest/brc_import.py`
- `biogpu/benchmarks/task_aligned_real.py`
- `configs/task_aligned_real.yaml`
- `configs/public_data_sources.yaml`
- `scripts/create_public_data_templates.py`
- `docs/V08_REAL_DATA_NOTES.md`
- `docs/TASK_ALIGNED_REAL_DATA.md`
- `docs/DANDI_DISCOVERY_PLAN.md`
- `docs/BRC_REPRODUCTION_PLAN.md`
- `research/PUBLIC_DATA_EVIDENCE_NOTES.md`

## Tests added in v0.8

- `tests/test_stimulus_windows.py`
- `tests/test_task_aligned_real_benchmark.py`
- `tests/test_dandi_discovery.py`
- `tests/test_brc_import.py`

## Status

v0.8 does not claim BioGPU advantage. It prepares the project to use public real spike datasets with honest stimulus-window alignment.


## v0.9 additions

- `biogpu/data_ingest/zenodo_manifest.py`
- `biogpu/data_ingest/nwb_stimulus_discovery.py`
- `biogpu/data_ingest/public_data_report.py`
- `biogpu/data_ingest/brc2602_import.py`
- `scripts/download_zenodo_14363732.py` updated
- `scripts/inspect_nwb_stimulus.py`
- `scripts/create_public_data_status_report.py`
- `docs/V09_REAL_PUBLIC_DATA_PLAN.md`
- `docs/ZENODO_14363732_WORKFLOW.md`
- `docs/DANDI_TASK_ALIGNED_WORKFLOW.md`
- `docs/BRC_2602_05737_REPRODUCTION_CONTRACT.md`
- `research/REAL_DATA_EVIDENCE_V09.md`
