# BioGPU-Core v2.3 Project Inventory

## New / updated v2.3 files

- `biogpu/benchmarks/registry_v23.py` — 44224 bytes
- `biogpu/benchmarks/biogpu_v23_benchmark_registry.py` — 531 bytes
- `tests/test_biogpu_v23_benchmark_registry.py` — 2237 bytes
- `docs/V23_BENCHMARK_REGISTRY.md` — 26579 bytes
- `benchmarks/BIOGPU_A1_BENCHMARK_REGISTRY.md` — 26579 bytes
- `benchmarks/BIOGPU_A1_BENCHMARK_REGISTRY.csv` — 2862 bytes
- `benchmarks/BIOGPU_A1_HARDWARE_READINESS_MATRIX.csv` — 3462 bytes
- `data/templates/v23_benchmark_task_manifest_template.json` — 1189 bytes
- `scripts/run_biogpu_v23_local_check.sh` — 1129 bytes
- `outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_benchmark_registry.json` — 35182 bytes
- `outputs/realdata_zenodo_14363732_v23_benchmark_registry/BIOGPU_V23_BENCHMARK_REGISTRY.md` — 26579 bytes
- `outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_benchmark_registry.csv` — 2862 bytes
- `outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_hardware_readiness_matrix.csv` — 3462 bytes
- `outputs/realdata_zenodo_14363732_v23_benchmark_registry/v23_benchmark_registry_summary.json` — 925 bytes
- `RUN_RESULTS_REALDATA_V23.md` — 2358 bytes
- `PROJECT_INVENTORY_V23.md` — MISSING

## v2.3 purpose

Add a formal Benchmark Registry layer above v2.2 hardware blueprint. The registry defines what must be measured before BioGPU can make claims about task performance, energy, latency, stability, or live wetware readiness.

## Registered benchmark task ids

- `B0_target_vs_random_electrode` — Target response separability — stage `offline_replay` — status `implemented`
- `B1_spot_localization` — Stimulus spot localization — stage `offline_replay` — status `requires_data`
- `B2_temporal_pattern_classification` — Temporal pattern classification — stage `dry_run` — status `ready_for_dry_run`
- `B3_orientation_like_encoding` — Orientation-like classification — stage `dry_run` — status `ready_for_dry_run`
- `B4_adaptive_closed_loop` — Adaptive closed-loop control — stage `future` — status `requires_live_lab`
- `B5_energy_latency_comparison` — Energy and latency comparison — stage `power_pc` — status `ready_for_dry_run`
- `B6_substrate_stability` — Substrate stability and drift — stage `licensed_lab` — status `requires_live_lab`

## Validation status

- Registry validation: OK
- Targeted pytest: 9 passed
- Live wetware claims: not made
