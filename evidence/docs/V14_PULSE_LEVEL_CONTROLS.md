# v1.4 — Pulse-level controls for Zenodo 14363732

## Why v1.4 exists

v1.3 established that the uploaded `Pre_processed_MEA_data.zip` contains real pulse-level stimulation protocol files:

```text
stimulation_protocols/*_stimulation_protocol.csv
```

Those files expose explicit:

```text
start, end, target
```

v1.4 adds the missing honesty layer: controls/null tests. The point is not only to show that the target electrode responds, but to test whether the result is stronger than plausible chance explanations.

## New modules

```text
biogpu/analysis/zenodo_pulse_controls.py
biogpu/benchmarks/zenodo_pulse_controls_analysis.py
tests/test_zenodo_pulse_controls.py
outputs/realdata_zenodo_14363732_v14_controls/
```

## Controls added

### 1. Same-recording random-electrode null

For each recording, v1.4 computes the pulse-aligned response delta for every electrode:

```text
response_delta = rate([stim_end, stim_end + response_window]) - rate([stim_start - response_window, stim_start])
```

Then it compares the true protocol target electrode against random non-target electrodes from the same recording.

This answers:

```text
Is the protocol target actually special, or would a random electrode look just as good?
```

### 2. Random-time-window null

For each recording, v1.4 keeps the true target electrode, but replaces true stimulus windows with random same-duration windows.

This answers:

```text
Is the response aligned to the true stimulation protocol, or is the target electrode generally active at random times too?
```

### 3. Spatial locality control

v1.4 also compares electrodes near the target against electrodes farther from the target:

```text
distance <= 1  vs  distance >= 3
```

This is a first-pass locality check. It is not yet a full spatial receptive-field model.

## CLI usage

```bash
python -m biogpu.benchmarks.zenodo_pulse_controls_analysis \
  /path/to/Pre_processed_MEA_data \
  --out outputs/realdata_zenodo_14363732_v14_controls \
  --response-window-ms 100 \
  --random-electrode-permutations 1000 \
  --random-time-permutations 300 \
  --seed 13
```

Optional plots can be requested with:

```bash
--plots
```

Plots are disabled by default because the benchmark should run reliably in headless/server environments.

## Real-data results from the uploaded archive

Input archive:

```text
Pre_processed_MEA_data.zip
```

Analyzed protocol recordings:

```text
recordings_with_target: 41
LightStim recordings: 38
ElecStim recordings: 3
```

Observed target response:

```text
median_target_response_percentile: 96.61016949152543
median_target_response_delta_rate_hz: 1.433333333333171
mean_target_response_delta_rate_hz: 3.26753974332656
```

Random-electrode null:

```text
permutations: 1000
median_random_electrode_percentile null median: 67.79661016949152
p_value_target_percentile_gt_random_electrode: 0.000999000999000999
p_value_target_delta_gt_random_electrode: 0.000999000999000999
```

Random-time-window null:

```text
permutations: 300
median_random_time_target_delta_rate_hz null median: 0.0
p_value_target_delta_gt_random_time_windows: 0.0033222591362126247
p_value_mean_target_delta_gt_random_time_windows: 0.0033222591362126247
```

LightStim-specific result:

```text
LightStim recordings: 38
median target percentile: 96.61016949152543
median target delta: 1.1333333333332796 Hz
same-recording random-electrode median percentile: 61.86440677966102
near-minus-far median delta: 0.6524637681158668 Hz
```

ElecStim-specific result:

```text
ElecStim recordings: 3
median target percentile: 89.83050847457628
median target delta: 10.000000000000009 Hz
same-recording random-electrode median percentile: 50.847457627118644
near-minus-far median delta: 6.492521367521372 Hz
```

## Honest interpretation

v1.4 makes the Zenodo result much stronger than v1.3:

```text
The true target electrode beats same-recording random electrodes.
The true stimulation timing beats randomized same-duration windows.
The response shows a first-pass spatial locality signal.
```

This supports a real pulse-aligned biological response signal.

But it is still not a claim that BioGPU outperforms GPUs or that we have a complete biological computer. The current claim is narrower and stronger:

```text
BioGPU-Core can reproducibly extract a statistically controlled, pulse-aligned target response from real public MEA data.
```

## Next step

v1.5 should move from response evidence to task evidence:

```text
1. Add culture/session-aware train/test splits.
2. Build a target-vs-nontarget or stimulated-site readout task.
3. Add label-shuffle controls for task accuracy.
4. Add NWB/DANDI adapter for task-aligned real datasets.
5. Add Allen Brain Observatory adapter for orientation-like benchmarks.
6. Inspect raw HDF5/TTL when raw Zenodo files are available.
```
