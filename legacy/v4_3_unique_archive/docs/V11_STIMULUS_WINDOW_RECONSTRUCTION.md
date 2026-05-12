# v1.1 — Stimulus-window reconstruction from Zenodo 14363732 metadata

## Result

The uploaded `Pre_processed_MEA_data.zip` allows **exact recording-level window reconstruction** but does **not** expose exact pulse-level stimulus timing.

## Exact recording-level windows

For every recording we can reconstruct:

- `start_s = 0.0`
- `end_s = recording_duration_sec`
- condition: `baseline`, `lightstim`, or `elecstim`
- target: light spot ID or stimulation electrode ID where encoded in the folder name

Snapshot:

```text
recording-level windows: 59
baseline: 18
lightstim: 38
elecstim: 3
quality: exact_recording_level
```

Light spots:

```text
13, 16, 26, 27, 34, 35, 41, 43, 45, 46, 47, 48,
54, 55, 61, 64, 67, 71, 73, 74, 75, 78, 82, 83, 87
```

Electrical stimulation electrodes:

```text
12, 51, 74
```

## Pulse-level windows

The metadata fields present in `meta_data.csv` are:

```text
recording_duration_sec
sampling_fr_hz
stimulation
scale_factor
peak_lifetime_period_ms
refractory_period_ms
```

There are no TTL/onset/offset fields such as:

```text
stim_start_s
stim_end_s
stim_onset_s
stim_offset_s
trigger_time
ttl_time
pulse_times
pulse_duration_s
pulse_period_s
```

Therefore pulse-level windows are **not reconstructable exactly** from the uploaded preprocessed metadata alone.

## Honest next step

1. Use the generated `recording_level_stimulus_windows.csv` for recording-level condition analysis only.
2. Do not claim pulse-level/PSTH results yet.
3. To build PSTH and true task-aligned benchmarks, obtain either:
   - raw HDF5 trigger/TTL channels, or
   - the original stimulation protocol from the paper/authors/code.

## Generated artifacts

```text
outputs/realdata_zenodo_14363732_stimulus_windows/recording_level_stimulus_windows.csv
outputs/realdata_zenodo_14363732_stimulus_windows/stimulus_window_reconstruction.json
outputs/realdata_zenodo_14363732_stimulus_windows/STIMULUS_WINDOW_RECONSTRUCTION_REPORT.md
```
