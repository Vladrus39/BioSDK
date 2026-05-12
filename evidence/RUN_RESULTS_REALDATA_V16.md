# RUN RESULTS — REALDATA v1.6

## Input

Used saved v1.5 pulse matrix:

```text
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv
```

Feature matrix:

```json
{
  "pulse_count": 11547,
  "feature_count": 354,
  "electrode_count": 59,
  "response_window_ms": 100.0,
  "cultures": 18,
  "conditions": {
    "elecstim": 180,
    "lightstim": 11367
  },
  "target_class_count": 27
}
```

## Parameters completed locally

```json
{
  "negative_counts": [
    1,
    3,
    5
  ],
  "ablation_negative_per_pulse": 3,
  "label_shuffles_completed": 10,
  "bootstrap_repeats_completed": 500,
  "seed": 101,
  "environment_limit_note": "In this ChatGPT/container run, 20+ shuffles for the full sweep exceeded the safe execution window. v1.6 records 10-shuffle local results and marks 100/1000-shuffle reruns in compute backlog."
}
```

## Negative-per-pulse sweep

| negatives/pulse | samples | ROC AUC | balanced acc | shuffle ROC AUC median | p(ROC AUC > shuffle) | culture-bootstrap AUC CI |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 23094 | 0.90113 | 0.79129 | 0.51585 | 0.09090909090909091 | 0.88864–0.94216 |
| 3 | 46188 | 0.90803 | 0.79299 | 0.52412 | 0.09090909090909091 | 0.89307–0.94587 |
| 5 | 69282 | 0.91103 | 0.79336 | 0.51867 | 0.09090909090909091 | 0.89805–0.94990 |

## Feature ablation

| feature set | n features | ROC AUC | balanced acc | shuffle ROC AUC median | p(ROC AUC > shuffle) | culture-bootstrap AUC CI |
|---|---:|---:|---:|---:|---:|---:|
| raw_candidate_counts_only | 4 | 0.92445 | 0.79990 | 0.53351 | 0.09090909090909091 | 0.91937–0.96973 |
| all_without_rank_zscore | 6 | 0.92443 | 0.79990 | 0.51527 | 0.09090909090909091 | 0.92282–0.96943 |
| all_features | 8 | 0.90677 | 0.79338 | 0.49298 | 0.09090909090909091 | 0.89419–0.94600 |
| exact_window_delta_only | 1 | 0.89974 | 0.85514 | 0.41136 | 0.09090909090909091 | 0.87024–0.97031 |
| within_pulse_rank_zscore_only | 2 | 0.59652 | 0.55561 | 0.47684 | 0.09090909090909091 | 0.54005–0.67806 |
| post_minus_pre_delta_only | 1 | 0.58009 | 0.62287 | 0.52096 | 0.09090909090909091 | 0.56934–0.66209 |
| pulse_context_only_negative_control | 2 | 0.50000 | 0.50000 | 0.50000 | 1.0 | 0.50000–0.50000 |

## Main interpretation

The target-vs-random-electrode readout remains strong when the task is made harder with 3 and 5 random non-target electrodes per pulse. The pulse-context-only negative control gives ROC AUC ≈ 0.5, as expected.

The strongest local ablation result is raw candidate counts only, suggesting that separability is not merely an artifact of rank/z-score engineered features.

## Compute honesty

This local run completed 10 label shuffles and 500 culture-bootstrap repeats. A 20+ shuffle full sweep exceeded the safe execution window in this environment. Required heavier reruns are listed in:

```text
docs/COMPUTE_BACKLOG.md
PROJECT_COMPUTE_BACKLOG_V16.md
```
