# BioGPU-Core v4.6 Master Project Plan — Clean Release Candidate

## Status

BioGPU-Core v4.6 is the clean, PC-ready release candidate. It is not another historical research archive. It is the package intended for transfer to a powerful PC/server to continue validation.

## What v4.6 fixes

1. Root documentation is consolidated.
2. Historical generated outputs are removed from the clean release.
3. Historical root `PROJECT_INVENTORY_V*` and `RUN_RESULTS_REALDATA_V*` files are removed from the clean package.
4. Current-only tests are placed under `tests/current`.
5. Full experimental data is registered as an external data asset instead of being embedded in the SDK.
6. A sample subset is included for smoke checks.
7. Power-PC deferred work is explicitly listed and scripted.
8. Docker/Compose defaults are updated to v4.6.

## Main entry points

- `README.md`
- `docs/POWERPC_TRANSFER_AND_VALIDATION_RUNBOOK_V46.md`
- `docs/DATA_ASSET_POLICY_V46.md`
- `docs/DATASET_API_EXPANSION_PLAN_V46.md`
- `docs/POWERPC_DEFERRED_WORK_ITEMS_V46.md`
- `beta/PRIVATE_BETA_QUICKSTART.md`

## Development stages after transfer to powerful PC

### Stage 0 — installation and reduced tests

Repeat reduced tests on the target PC:

```bash
bash scripts/run_biogpu_v46_powerpc_smoke.sh
```

Validate the full preprocessed dataset asset:

```bash
mkdir -p data/external
cp /path/to/Pre_processed_MEA_data.zip data/external/Pre_processed_MEA_data.zip
bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip
```

### Stage 1 — compact replay validation

Repeat compact lineage-strict sweeps using the same logic developed here.

### Stage 2 — full statistics

Run `full_shuffle_1000` with lineage-strict split, sklearn readouts, ablations and bootstrap CI.

### Stage 3 — extended methods

Run `extended_methods_5000` only after Stage 2 is stable.

### Stage 4 — raw data / TTL

Download raw HDF5 archive, inspect TTL/stimulus channels, reconstruct windows and compare raw-derived windows with preprocessed pipeline.

### Stage 5 — dataset/API expansion

Add DANDI/NWB and AllenSDK benchmarks, then FinalSpark/vendor read-only exports if credentials/data are available.

### Stage 6 — latency/energy measurement

Measure host latency and energy on fixed workloads.

### Stage 7 — beta release gate

Generate final PC result bundle and decide whether external private beta is justified.

## Commercial release path

1. Developer Evaluation: local SDK, sample data, replay.
2. Research Pilot: maximum safe software access, own data, read-only APIs.
3. Enterprise Read-Only: hosted/on-prem, team access, support.
4. Live Shadow: live read stream without actuation.
5. Lab-Approved Closed Loop: separate approved module only.

## Safety boundary

Full software access is acceptable for early testers. Unapproved biological actuation is not.

Blocked by default:

- electrode actuation
- live stimulation commands
- pinout/wiring instructions
- wet-lab environment/media control
- uncontrolled closed-loop actuation

