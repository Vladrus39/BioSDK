# RUN_RESULTS_REALDATA_V12

## Dataset

Uploaded public dataset: `Pre_processed_MEA_data.zip` from Zenodo 14363732.

## Analysis status

This release performs recording-level condition and spot-level response analysis.

It does **not** claim pulse-level PSTH because the preprocessed metadata does not include TTL/onset/offset timing fields.

## Key results

- Baseline vs LightStim leave-one-culture accuracy: 0.511
- Baseline vs LightStim stratified 5-fold accuracy: 0.300
- LightStim recordings with matching baseline: 38
- Target spot/electrode present: 38
- Median target delta rate: 0.615 Hz
- Mean target delta rate: 0.378 Hz
- Median target delta percentile: 91.38%
- Exploratory repeated-spot classification accuracy: 0.042 vs approx chance 0.10

## Interpretation

Condition-level classification is weak with the current aggregate recording features.

However, the target spot/electrode response profile is strong: the stimulated spot/electrode tends to rank high among electrode-level delta responses compared with the culture baseline.

This is real biological signal, but it remains recording-level evidence. The next step is raw HDF5/TTL inspection or protocol recovery for pulse-level stimulus windows.
