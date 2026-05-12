# BioGPU-Core v5.15 DANDI/NWB Task Validation Guide

v5.15 validates the first real DANDI/NWB sample downloaded for the BioSDK proof path.

It checks that a local NWB file exposes spike units, trial/interval metadata, stimulus metadata, and exportable task windows. This is the first concrete external public-data parser proof beyond the Zenodo MEA source family.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v515_dandi_nwb_task_validation.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Outputs

- `outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json`
- `outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_SAMPLE_REPORTS.json`
- `outputs/v515_dandi_nwb_task_validation/V515_DANDI_NWB_TASK_WINDOWS.csv`
- `outputs/v515_dandi_nwb_task_validation/BIOGPU_V515_DANDI_NWB_TASK_VALIDATION_REPORT.md`

## Boundary

This validates local DANDI/NWB parser portability and task-window export for one downloaded sample. It does not prove full multi-dataset BioSDK, external read-only API validation, production runtime, or BiC OS readiness.
