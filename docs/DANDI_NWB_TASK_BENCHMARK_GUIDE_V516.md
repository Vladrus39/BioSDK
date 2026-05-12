# BioGPU-Core v5.16 DANDI/NWB Task Benchmark Guide

v5.16 turns the first validated DANDI/NWB sample into a public BioSDK benchmark example.

The benchmark reads spike units from the NWB file, builds per-trial spike-count and firing-rate features, predicts the task `loads` label with a stratified nearest-centroid readout, and compares the observed balanced accuracy to shuffled-label controls.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v516_dandi_nwb_task_benchmark.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Example

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' .\examples\biosdk_v516_dandi_task_benchmark.py
```

## Outputs

- `outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json`
- `outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_FEATURE_MATRIX.npz`
- `outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TRIAL_FEATURES.csv`
- `outputs/v516_dandi_nwb_task_benchmark/V516_DANDI_NWB_TASK_READOUT.json`
- `outputs/v516_dandi_nwb_task_benchmark/BIOGPU_V516_DANDI_NWB_TASK_BENCHMARK_REPORT.md`

## Boundary

This is a single-sample public NWB SDK benchmark. It proves the parser, task-window export, feature matrix and readout workflow on one DANDI sample. It does not prove full BioSDK, multi-dataset generalization, external API validation, production runtime or BiC OS readiness.
