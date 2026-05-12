# v1.2 — Condition and spot-level real-data analysis

This release performs the first condition/spot response analysis on the uploaded `Pre_processed_MEA_data.zip` dataset.

## What is valid

- Recording-level baseline / LightStim / ElecStim labels.
- LightStim spot IDs parsed from folder names and metadata.
- Culture-matched baseline-vs-LightStim electrode-rate deltas.
- Spot-level response profile under the assumption that spot IDs map to MEA grid/electrode positions.

## What is not valid yet

- Pulse-triggered PSTH.
- Exact LightStim onset/offset windows.
- Per-pulse evoked response claims.
- Energy-per-task advantage claims.

## Results

- Baseline vs LightStim leave-one-culture accuracy: 0.511.
- Baseline vs LightStim stratified 5-fold accuracy: 0.300.
- Median target delta percentile: 91.38%.
- Repeated-spot exploratory classification: 0.042 vs approx chance 0.10.

## Interpretation

The condition-level classifier is weak. The spot-level response profile is much more interesting: the target spot/electrode shows high delta percentile relative to the rest of the MEA after subtracting the matched culture baseline.

This suggests that the LightStim labels carry a real spatial response signal, but not enough to claim spot classification with the current recording-level features.

## Next step

Inspect raw HDF5 files or original stimulation protocol to reconstruct pulse-level `stimulus_windows.csv` and compute PSTH.
