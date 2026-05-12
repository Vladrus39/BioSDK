# BioGPU-Core v1.3 — Zenodo pulse-level stimulus windows

## Main correction after v1.2

v1.2 treated the uploaded Zenodo preprocessed archive as recording-level only. That was too conservative.

The actual uploaded `Pre_processed_MEA_data.zip` contains per-recording folders:

```text
stimulation_protocols/*_stimulation_protocol.csv
```

These CSV files contain explicit:

```text
start    end    target
```

The values are in milliseconds in the uploaded archive, inferred because values such as `1869.65` cannot be seconds inside a `604.5 s` recording. They convert to `1.86965 s`.

## What v1.3 adds

```text
biogpu/data_ingest/zenodo_protocol_windows.py
biogpu/analysis/zenodo_pulse_level.py
biogpu/benchmarks/zenodo_pulse_level_analysis.py
tests/test_zenodo_protocol_windows.py
tests/test_zenodo_pulse_level_analysis.py
outputs/realdata_zenodo_14363732_v13_pulse/
```

## New command

```bash
PYTHONPATH=. python -m biogpu.benchmarks.zenodo_pulse_level_analysis \
  /path/to/extracted/Pre_processed_MEA_data \
  --out outputs/realdata_zenodo_14363732_v13_pulse \
  --response-window-ms 100
```

## Generated v1.3 artifacts

```text
outputs/realdata_zenodo_14363732_v13_pulse/stimulus_windows.csv
outputs/realdata_zenodo_14363732_v13_pulse/protocol_windows_summary.json
outputs/realdata_zenodo_14363732_v13_pulse/pulse_response_by_recording.csv
outputs/realdata_zenodo_14363732_v13_pulse/pulse_response_summary.json
outputs/realdata_zenodo_14363732_v13_pulse/PULSE_LEVEL_ANALYSIS_REPORT.md
outputs/realdata_zenodo_14363732_v13_pulse/pulse_target_response_percentile_hist.png
outputs/realdata_zenodo_14363732_v13_pulse/pulse_target_response_delta_by_spot.png
outputs/realdata_zenodo_14363732_v13_pulse/pulse_near_vs_far_response_delta.png
```

## Real run result on uploaded data

### Protocol-window discovery

```json
{
  "pulse_window_count": 11547,
  "recording_count_with_protocols": 41,
  "by_condition": {
    "lightstim": 11367,
    "elecstim": 180
  },
  "inferred_time_units": {
    "ms": 11547
  },
  "mean_duration_ms": 22.77776478739106,
  "min_duration_ms": 0.3000000000383807,
  "max_duration_ms": 40.000000000020464
}
```

### Pulse-aligned response analysis

Response window after stimulus end: `100 ms`.

```json
{
  "recordings_with_protocols": 41,
  "by_condition_recordings": {
    "lightstim": 38,
    "elecstim": 3
  },
  "by_condition_pulses": {
    "lightstim": 11367,
    "elecstim": 180
  },
  "target_electrode_present_count": 41,
  "lightstim": {
    "recordings": 38,
    "mean_target_response_delta_rate_hz": 2.7009420037646206,
    "median_target_response_delta_rate_hz": 1.1333333333332796,
    "median_target_response_percentile": 96.61016949152543,
    "mean_target_pulse_fraction_response_gt_pre": 0.28598401531544093,
    "median_target_exact_delta_rate_hz": 147.41415224950296
  },
  "elecstim": {
    "recordings": 3,
    "mean_target_response_delta_rate_hz": 10.444444444444452,
    "median_target_response_delta_rate_hz": 10.000000000000009,
    "median_target_response_percentile": 89.83050847457628,
    "mean_target_pulse_fraction_response_gt_pre": 0.9666666666666667,
    "median_target_exact_delta_rate_hz": 0.0
  }
}
```

## Meaning

v1.3 is the first true pulse-level real-data step in this project.

It supports:

```text
real protocol pulse windows → spike alignment → target electrode response profile
```

It does **not** yet support:

```text
BioGPU beats GPU/CPU
full energy-per-task benchmark
publication-grade causal TTL proof
cross-dataset generalization claim
```

## Next honest step

1. Inspect raw HDF5/TTL to independently verify protocol timing.
2. Add pulse-level PSTH plots per recording and per spot.
3. Build a train/test readout using pulse windows, not aggregate recording labels.
4. Add DANDI NWB task-aligned parser once the actual NWB files are available locally.
5. Add Allen Brain Observatory visual benchmark adapter once data access/download is configured.
