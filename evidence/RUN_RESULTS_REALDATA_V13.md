# BioGPU-Core real-data run — v1.3 pulse-level Zenodo analysis

Input archive used locally:

```text
Pre_processed_MEA_data.zip
```

Project archive updated from:

```text
biogpu-core-v1_2_condition_spot.zip
```

## Command

```bash
PYTHONPATH=. python -m biogpu.benchmarks.zenodo_pulse_level_analysis \
  /mnt/data/biogpu_work/preprocessed \
  --out outputs/realdata_zenodo_14363732_v13_pulse \
  --response-window-ms 100
```

## Main finding

The preprocessed dataset contains exact protocol CSV files:

```text
stimulation_protocols/*_stimulation_protocol.csv
```

Therefore the v1.2 statement that pulse-level windows require raw HDF5 was too conservative. Raw HDF5/TTL remains important for independent verification, but v1.3 can already build pulse-level windows from the uploaded preprocessed archive.

## Results

```json
{
  "protocol_summary": {
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
  },
  "pulse_response_summary": {
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
}
```

## Tests

Focused v1.3 tests:

```text
8 passed
```

Full project test run:

```text
Not completed inside the build timeout. The existing slow benchmark tests start running but exceed the available execution window. Focused v1.3 regression tests passed.
```

## Honest conclusion

Zenodo 14363732 now provides a real pulse-level signal path for BioGPU-Core:

```text
protocol CSV start/end/target → pulse stimulus_windows.csv → spike alignment → target response deltas
```

This is stronger than v1.2 recording-level evidence. It is still not a claim that BioGPU outperforms conventional computing.
