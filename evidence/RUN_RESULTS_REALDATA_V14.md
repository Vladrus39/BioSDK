# RUN_RESULTS_REALDATA_V14

## Command

```bash
python -m biogpu.benchmarks.zenodo_pulse_controls_analysis \
  /mnt/data/preprocessed_mea_v14 \
  --out outputs/realdata_zenodo_14363732_v14_controls \
  --response-window-ms 100 \
  --random-electrode-permutations 1000 \
  --random-time-permutations 300 \
  --seed 13
```

## Test command

```bash
pytest -q \
  tests/test_zenodo_pulse_controls.py \
  tests/test_zenodo_pulse_level_analysis.py \
  tests/test_zenodo_protocol_windows.py \
  tests/test_zenodo_condition_spot_analysis.py \
  tests/test_zenodo_preprocessed_real.py \
  tests/test_zenodo_stimulus_reconstruction.py \
  tests/test_brc2602_contract.py \
  tests/test_dandi_nwb_adapter.py
```

## Test result

```text
15 passed in 1.72s
```

## Real-data result summary

```json
{
  "recordings_with_target": 41,
  "observed": {
    "median_target_response_percentile": 96.61016949152543,
    "median_target_response_delta_rate_hz": 1.433333333333171,
    "mean_target_response_delta_rate_hz": 3.26753974332656
  },
  "random_electrode_null": {
    "permutations": 1000,
    "median_random_electrode_percentile_null_median": 67.79661016949152,
    "p_value_target_percentile_gt_random_electrode": 0.000999000999000999,
    "p_value_target_delta_gt_random_electrode": 0.000999000999000999
  },
  "random_time_window_null": {
    "permutations": 300,
    "median_random_time_target_delta_rate_hz_null_median": 0.0,
    "p_value_target_delta_gt_random_time_windows": 0.0033222591362126247,
    "p_value_mean_target_delta_gt_random_time_windows": 0.0033222591362126247
  }
}
```

## Output files

```text
outputs/realdata_zenodo_14363732_v14_controls/PULSE_LEVEL_CONTROLS_REPORT.md
outputs/realdata_zenodo_14363732_v14_controls/pulse_control_summary.json
outputs/realdata_zenodo_14363732_v14_controls/pulse_electrode_response_by_recording.csv
outputs/realdata_zenodo_14363732_v14_controls/pulse_recording_controls.csv
outputs/realdata_zenodo_14363732_v14_controls/random_electrode_null_distribution.csv
outputs/realdata_zenodo_14363732_v14_controls/random_time_window_null_distribution.csv
```

## Honest conclusion

v1.4 confirms that the target-electrode pulse-aligned response is not explained by a simple random-electrode null or random-time-window null. This is a stronger real-data biological response result than v1.3.

This is still not a full BioGPU computational advantage benchmark. It is a controlled pulse-response benchmark and should be used as the foundation for v1.5 task/readout benchmarks.
