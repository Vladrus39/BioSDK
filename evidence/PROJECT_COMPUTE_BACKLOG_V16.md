# Project compute backlog v1.6

This is the short operational checklist of tasks that should be moved to stronger compute and not forgotten.

## Must rerun later

1. `v1.6 --label-shuffles 100` for negative sweep and ablation.
2. `v1.6 --label-shuffles 1000` for final null-baseline p-values.
3. Rebuild v1.5 feature matrix directly from `Pre_processed_MEA_data` and compare with saved `pulse_feature_matrix.npz`.
4. Download Zenodo raw HDF5 and verify TTL/trigger/stimulation channels.
5. Build TTL-derived pulse windows and compare them to `stimulation_protocol.csv` start/end/target windows.
6. Run DANDI 000469 NWB adapter on real downloaded NWB files.
7. Run Allen Brain Observatory orientation benchmark on a controlled downloaded subset.
8. Add logistic regression / linear SVM readouts with culture-aware validation.
9. Repeat negative sampling over many random seeds.
10. Run response-window sweep: 20, 50, 100, 200, 500 ms.

## Current local limitation recorded

The ChatGPT/container environment was enough for:

- loading v1.5 matrix;
- v1.6 negative sweep for 1/3/5 negatives per pulse with 10 label shuffles;
- 500 culture-bootstrap repeats;
- feature ablation with 10 label shuffles.

The environment was not enough for a full 20/100/1000-shuffle v1.6 sweep within the safe execution window. This is why the archive includes fast-path CLI and backlog instructions.
