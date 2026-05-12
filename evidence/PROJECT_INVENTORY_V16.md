# PROJECT INVENTORY v1.6

## New code

- `biogpu/analysis/zenodo_pulse_v16.py` — robustness tools: load v1.5 matrix, negative-per-pulse sweep, culture bootstrap CI, feature ablation.
- `biogpu/benchmarks/zenodo_pulse_v16_analysis.py` — CLI that can rebuild from raw preprocessed root.
- `biogpu/benchmarks/zenodo_pulse_v16_from_v15.py` — fast CLI from saved v1.5 matrix.

## New tests

- `tests/test_zenodo_pulse_v16.py`

## New docs

- `docs/V16_PULSE_READOUT_ROBUSTNESS.md`
- `docs/COMPUTE_BACKLOG.md`
- `PROJECT_COMPUTE_BACKLOG_V16.md`
- `RUN_RESULTS_REALDATA_V16.md`

## New outputs

- `outputs/realdata_zenodo_14363732_v16_robustness/v16_readout_robustness_summary.json`
- `outputs/realdata_zenodo_14363732_v16_robustness/negative_sweep_details.json`
- `outputs/realdata_zenodo_14363732_v16_robustness/feature_ablation_details.json`
- `outputs/realdata_zenodo_14363732_v16_robustness/negative_per_pulse_sweep.csv`
- `outputs/realdata_zenodo_14363732_v16_robustness/feature_ablation.csv`
- `outputs/realdata_zenodo_14363732_v16_robustness/PULSE_LEVEL_READOUT_ROBUSTNESS_REPORT.md`

## Version purpose

v1.6 does not add a new biological claim. It strengthens v1.5 by checking that the target-vs-random-electrode separability survives harder negative sampling and feature ablation.
