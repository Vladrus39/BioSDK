# BioGPU-Core compute backlog

This file records experiments that should be rerun on stronger compute or with longer wall-clock limits. It prevents unfinished heavy work from being lost.

## Immediate v1.6 reruns

| Priority | Item | Why it matters | Recommended command / notes | Expected cost |
|---:|---|---|---|---|
| P0 | Rerun v1.6 full shuffle baseline with 100 label shuffles | Current local v1.6 completed 10 shuffles for the full negative sweep/ablation. More shuffles give stronger p-value resolution. | `python -m biogpu.benchmarks.zenodo_pulse_v16_from_v15 outputs/realdata_zenodo_14363732_v15_readout --out outputs/realdata_zenodo_14363732_v16_robustness_100shuf --negative-counts 1,3,5 --ablation-negative-per-pulse 3 --label-shuffles 100 --bootstrap-repeats 2000` | CPU-heavy, no GPU required |
| P0 | Rerun v1.6 with 1000 label shuffles for final paper-grade null | Gives p-value resolution around 0.001. | Same as above with `--label-shuffles 1000 --bootstrap-repeats 5000` | Strong CPU / long job |
| P0 | Rebuild v1.5 feature matrix from raw preprocessed spike CSV, then compare hash/shape to saved matrix | Confirms that v1.6 fast-path matrix is reproducible from source CSV. | `python -m biogpu.benchmarks.zenodo_pulse_readout_analysis <Pre_processed_MEA_data> --out outputs/rebuild_v15_check --candidate-label-shuffles 0 --target-label-shuffles 0` then compare `pulse_feature_matrix.npz`. | Slow CSV parsing |

## Raw HDF5 / TTL verification

| Priority | Item | Why it matters | Notes | Expected cost |
|---:|---|---|---|---|
| P0 | Download and inspect Zenodo raw HDF5 | Needed for independent TTL/trigger verification of `stimulation_protocol.csv` windows. | Search for HDF5 groups/channels containing TTL, trigger, stim, digital input, events. | Large download + HDF5 scan |
| P0 | Build `pulse_windows_from_ttl.csv` and compare to protocol CSV | Confirms that protocol windows are aligned to recorded acquisition time, not just planned stimulation time. | Compute start/end deltas, missing pulses, duplicates. | CPU + storage |
| P1 | Add TTL-vs-protocol discrepancy report | Required before strong claims in a paper/preprint. | JSON + markdown report. | Moderate |

## External real-data expansion

| Priority | Item | Why it matters | Notes | Expected cost |
|---:|---|---|---|---|
| P0 | DANDI 000469 NWB parser run on real NWB files | Needed for real task-aligned benchmark beyond Zenodo spot response. | Parse `units`, `trials/intervals`, stimulus/task labels. | Download + CPU |
| P1 | Allen Brain Observatory orientation benchmark | Real V1 orientation analog of synthetic tests. | Need controlled subset and cached manifest. | Large download |
| P1 | BRC 2602.05737 data/code reproduction if released | Closest external biological-reservoir benchmark target. | Verify data availability and license. | Unknown |

## Model/readout expansion

| Priority | Item | Why it matters | Notes | Expected cost |
|---:|---|---|---|---|
| P1 | Logistic regression / linear SVM readout with culture-aware CV | Tests whether simple centroids understate performance. | Use nested regularization within training cultures only. | CPU moderate |
| P1 | Multiple negative sampling repeats | Current v1.6 samples one random set per run. Repeat seeds and aggregate. | 20–100 seeds. | CPU-heavy |
| P2 | Time-window ablation: 20/50/100/200/500 ms | Finds optimal response window and prevents cherry-picking. | Run v1.5/v1.6 for each window. | CPU-heavy |
| P2 | Per-culture failure analysis | Identifies cultures that do not transfer or dominate. | Plot fold-level AUCs and target distributions. | Light |

## Hardware notes

- No GPU is required for the current v1.3-v1.6 centroid/readout pipeline.
- Strong CPU and enough RAM/storage are more important for raw HDF5/NWB and large shuffle runs.
- GPU becomes useful only if we add neural network readouts, large-scale embedding models, or heavy Allen/NWB preprocessing.


## v1.7 additions

See `PROJECT_COMPUTE_BACKLOG_V17.md` and `docs/V17_PAPER_GRADE_RERUN_PLAN.md` for the full stronger-readout rerun plan.
