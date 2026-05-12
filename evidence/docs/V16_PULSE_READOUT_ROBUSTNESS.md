# v1.6 — Pulse-level readout robustness

v1.6 extends v1.5 by making the pulse-level readout harder and more transparent.

## Added

- `biogpu/analysis/zenodo_pulse_v16.py`
- `biogpu/benchmarks/zenodo_pulse_v16_analysis.py`
- `biogpu/benchmarks/zenodo_pulse_v16_from_v15.py`
- `tests/test_zenodo_pulse_v16.py`
- `outputs/realdata_zenodo_14363732_v16_robustness/`
- `docs/COMPUTE_BACKLOG.md`
- `PROJECT_COMPUTE_BACKLOG_V16.md`

## Why a fast-path from v1.5 matrix exists

Rebuilding the pulse matrix from spike CSV files can be slow in a constrained notebook/container environment. v1.5 already writes:

- `pulse_feature_matrix.npz`
- `pulse_feature_metadata.csv`

v1.6 can load those files and run robustness checks without reparsing all spike CSV files.

## Main checks

1. Negative-per-pulse sweep: true target electrode vs 1, 3, and 5 random non-target electrodes from the same pulse.
2. Culture-bootstrap confidence intervals over leave-one-culture folds.
3. Feature ablation: raw counts, exact-window delta, post/pre delta, rank/z-score features, and pulse-context negative control.

## Interpretation

v1.6 supports the claim that real pulse-aligned spike features contain cross-culture separability for the stimulated target electrode. It does not prove BioGPU advantage over silicon GPUs.

## Compute honesty

The archive records local 10-shuffle results and explicitly lists heavier 100/1000-shuffle reruns in `docs/COMPUTE_BACKLOG.md`.
