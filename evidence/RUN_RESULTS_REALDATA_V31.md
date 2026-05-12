# RUN RESULTS — BioGPU-Core v3.1 End-to-End Integration

## Scope

v3.1 performs a deterministic software-only integration run:

```text
manifest -> encoder -> replay observation -> readout -> energy/latency -> result bundle
```

## Local checks

Expected checks:

- py_compile: OK
- v3.1 E2E run: OK
- targeted pytest: OK

## Generated output directory

`outputs/realdata_zenodo_14363732_v31_e2e/`

Main artifacts:

- `run_manifest_v31.json`
- `encoded_pattern_v31.json`
- `replay_observation_v31.json`
- `readout_feature_batch_v31.json`
- `readout_prediction_v31.json`
- `energy_latency_report_v31.json`
- `baseline_comparison_v31.csv`
- `audit_log_v31.jsonl`
- `BIOGPU_V31_E2E_REPORT.md`
- `e2e_summary_v31.json`
- `biogpu_v31_e2e_result_bundle.zip`

## Boundary

v3.1 does not prove live BioGPU operation and does not prove GPU advantage. It verifies that the software stack can be run under one auditable manifest.
