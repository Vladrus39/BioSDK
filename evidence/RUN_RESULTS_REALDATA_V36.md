# BioGPU-Core v3.6 Run Results

Status: `COMPLETED_LOCAL_COMPACT_VALIDATION`

## Local compact validation

Command:

```bash
bash scripts/run_biogpu_v36_local_check.sh
```

Results:

```text
py_compile: OK
pytest tests/test_biogpu_v36_lineage_bootstrap.py: 3 passed
v3.6 compact runner: OK
```

Dataset profile:

```text
rows / pulse windows: 11,547
features: 354
culture labels: 18
base lineages parsed: 10
target classes: 27
conditions: elecstim, lightstim
```

Compact local lineage-strict run:

```text
split_count: 3
sweep_run_count: 6
best split: lineage_holdout_offset_0
best decoder: diag_gaussian
best ablation: response_delta_count
accuracy: 0.475000
balanced_accuracy: 0.598333
chance_approx: 0.500000
shuffle_mean_accuracy: 0.432407
improvement_vs_shuffle_mean: 0.042593
empirical_p_value_shuffled_ge_real: 0.500000
```

Interpretation:

v3.6 is primarily a statistical-hardening release, not a new performance claim. It proves that the code can build base-lineage holdout splits where all DIV variants of a base lineage remain entirely on one side of train/test. This is required before large power-PC sweeps.

## Boundary

This remains software-only public-data replay. It does not prove live BioGPU, GPU advantage, wet-lab operation, or approved stimulation.
