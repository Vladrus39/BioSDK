# BioGPU-Core v5.20 Allen Orientation Benchmark Guide

v5.20 turns a validated Allen visual-coding NWB session into a bounded BioSDK benchmark.

It uses `drifting_gratings_presentations`, extracts finite `orientation` labels, selects the highest-rate units, builds spike-count/rate features, and evaluates a stratified nearest-centroid orientation readout against shuffled-label controls.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v520_allen_orientation_benchmark.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' -TopUnits 64 -MaxWindows 800 -LabelShuffles 100
```

## Outputs

- `outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json`
- `outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_FEATURE_MATRIX.npz`
- `outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_TRIAL_FEATURES.csv`
- `outputs/v520_allen_orientation_benchmark/V520_ALLEN_ORIENTATION_READOUT.json`
- `outputs/v520_allen_orientation_benchmark/BIOGPU_V520_ALLEN_ORIENTATION_BENCHMARK_REPORT.md`

## Boundary

This is a single-session public Allen benchmark. It strengthens BioSDK evidence, but it does not prove full multi-dataset SDK readiness or BiC OS readiness.
