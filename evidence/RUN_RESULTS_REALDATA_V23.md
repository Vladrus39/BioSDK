# BioGPU-Core v2.3 — Benchmark Registry Run Results

Date: 2026-05-04

## Scope

v2.3 converts the BioGPU-A1 hardware blueprint into a formal benchmark registry. Each registered task now includes:

- input contract
- encoder contract
- substrate requirement
- readout contract
- metrics
- controls
- success gates
- known failure modes
- hardware/readiness mapping

## Generated outputs

Output directory:

```text
outputs/realdata_zenodo_14363732_v23_benchmark_registry/
```

Files:

```text
biogpu_v23_benchmark_registry.json
BIOGPU_V23_BENCHMARK_REGISTRY.md
biogpu_v23_benchmark_registry.csv
biogpu_v23_hardware_readiness_matrix.csv
v23_benchmark_registry_summary.json
```

## Registry summary

```json
{
  "version": "v2.3",
  "tasks": 7,
  "stages": [
    "dry_run",
    "future",
    "licensed_lab",
    "offline_replay",
    "power_pc"
  ],
  "implemented_tasks": [
    "B0_target_vs_random_electrode"
  ],
  "dry_run_ready_tasks": [
    "B2_temporal_pattern_classification",
    "B3_orientation_like_encoding",
    "B5_energy_latency_comparison"
  ],
  "live_lab_tasks": [
    "B4_adaptive_closed_loop",
    "B6_substrate_stability"
  ],
  "validation_errors": [],
  "outputs": {
    "json": "outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_benchmark_registry.json",
    "markdown": "outputs/realdata_zenodo_14363732_v23_benchmark_registry/BIOGPU_V23_BENCHMARK_REGISTRY.md",
    "csv": "outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_benchmark_registry.csv",
    "readiness_csv": "outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_hardware_readiness_matrix.csv"
  }
}
```

## Validation

Registry validation errors:

```text
[]
```

Expected result: empty list.

## Checks performed in this package build

Targeted Python compile check:

```text
py_compile: OK
```

Registry generation:

```text
python -m biogpu.benchmarks.biogpu_v23_benchmark_registry --out-dir outputs/realdata_zenodo_14363732_v23_benchmark_registry
result: OK
```

Targeted pytest:

```text
python -m pytest -q tests/test_biogpu_v23_benchmark_registry.py tests/test_biogpu_v22_hardware_blueprint.py
result: 9 passed in 0.90s
```

A convenience wrapper is included:

```bash
bash scripts/run_biogpu_v23_local_check.sh
```

## Boundary

v2.3 still does not emit live biological stimulation parameters, wet-lab protocols, vendor pinouts or safety limits. It defines benchmark contracts and evidence gates only.
