# Run results — BioGPU-Core v1.7

## Input

Fast path from:

```text
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz
outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv
```

No raw spike CSV reparse was performed for the included v1.7 quick run.

## Feature matrix

```text
pulse windows: 11,547
features: 354
electrodes: 59
cultures: 18
conditions: lightstim 11,367; elecstim 180
target classes: 27
```

## Included local quick run

```text
negative_per_pulse: 1
negative_seed: 101
readout: logistic_l2
feature_set: raw_candidate_counts_only
label_shuffles: 1
candidate samples: 23,094
positive fraction: 0.5
observed ROC AUC: 0.9233371147618595
observed balanced accuracy: 0.8597471204641898
single shuffle ROC AUC: 0.5212919273547223
single shuffle balanced accuracy: 0.5246817355157183
```

## Interpretation

This confirms that a stronger linear readout on raw spike-count features remains highly separable above a quick shuffled baseline.

The run is intentionally labelled `local_quick`. It is not the final publication-grade permutation run. The full run plan is in:

```text
docs/V17_PAPER_GRADE_RERUN_PLAN.md
PROJECT_COMPUTE_BACKLOG_V17.md
```

## Checks performed

```text
py_compile OK
manual v1.7 toy smoke tests OK
local quick real-data run OK
```

`pytest` was not reported as a clean full-suite run in this environment because earlier broad test invocations timed out under container limits.
