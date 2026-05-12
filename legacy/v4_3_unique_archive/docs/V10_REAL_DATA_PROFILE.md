# v1.0-realdata — first real MEA data profile

This release adds a parser and profile report for the uploaded Zenodo `14363732` preprocessed MEA dataset.

## What changed

- Added `biogpu/data_ingest/zenodo_mea2100_preprocessed.py`.
- Added `biogpu/benchmarks/zenodo_real_dataset_profile.py`.
- Added tests for the sample-number CSV parser.
- Generated first real-data profile outputs under `outputs/realdata_zenodo_14363732/`.

## Uploaded dataset

The uploaded archive `Pre_processed_MEA_data.zip` contains per-electrode CSV files with a `sample_num` column and `metadata/meta_data.csv` for each recording. The parser converts sample numbers to seconds using the sampling frequency from metadata, typically 20 kHz.

## Real profile snapshot

- Recordings: 59
- Cultures: 18
- Plate IDs: 10
- Conditions: 18 baseline, 41 light-stimulation
- Total spikes: 3,124,346
- Median recording duration: 605.4 s
- Median active electrodes: 51
- Median spikes per recording: 36,800
- Median array firing rate: 64.59 Hz

## Exploratory condition benchmark

A recording-level baseline-vs-light-stimulation classifier was run using aggregate spike features.

- Leave-one-culture-out accuracy: 0.661
- Stratified 5-fold accuracy, leakage-prone: 0.659
- Confusion matrix [baseline, lightstim]: `[[14, 4], [16, 25]]`

This is **not** a BRC-style stimulus-window benchmark. It is only a real-data profiling/classification sanity check.

## Next step

Reconstruct exact stimulus windows from raw metadata or experiment protocol, then run true task-aligned spike-window classification.
