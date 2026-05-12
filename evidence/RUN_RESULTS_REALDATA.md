# RUN RESULTS — Real Data v1.0

## Dataset

Uploaded file: `Pre_processed_MEA_data.zip` from Zenodo 14363732.

## Profile command

```bash
python -m biogpu.benchmarks.zenodo_real_dataset_profile /path/to/zenodo_preprocessed
```

The current project stores generated results in:

```text
outputs/realdata_zenodo_14363732/
```

## Main results

- Recordings: 59
- Cultures: 18
- Plate IDs: 10
- Conditions: 18 baseline, 41 lightstim
- Total spikes: 3,124,346
- Median duration: 605.4 s
- Median active electrodes: 51.0
- Median spikes per recording: 36,800
- Median array firing rate: 64.59 Hz

## Exploratory benchmark

Recording-level baseline vs lightstimulation classification:

- Leave-one-culture-out accuracy: 0.661
- Stratified 5-fold accuracy, leakage-prone: 0.659

Honesty note: this is not a final BioGPU benchmark. It is real spike-data ingestion/profile evidence.

---

# v1.1 Stimulus-window reconstruction

Result: exact **recording-level** windows reconstructed from metadata/folder labels.

```text
recording-level windows: 59
baseline: 18
lightstim: 38
elecstim: 3
quality: exact_recording_level
```

Pulse-level windows: **not reconstructable exactly** from `Pre_processed_MEA_data.zip` metadata alone.

Reason: metadata contains only:

```text
recording_duration_sec, sampling_fr_hz, stimulation, scale_factor,
peak_lifetime_period_ms, refractory_period_ms
```

No TTL/onset/offset/pulse timing fields were found.

Generated:

```text
outputs/realdata_zenodo_14363732_stimulus_windows/recording_level_stimulus_windows.csv
outputs/realdata_zenodo_14363732_stimulus_windows/stimulus_window_reconstruction.json
outputs/realdata_zenodo_14363732_stimulus_windows/STIMULUS_WINDOW_RECONSTRUCTION_REPORT.md
```
