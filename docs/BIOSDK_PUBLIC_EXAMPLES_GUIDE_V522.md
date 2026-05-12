# BioGPU-Core v5.22 BioSDK Public Examples Guide

v5.22 packages the proven public BioSDK path into runnable examples and a machine-readable runbook.

It covers the local safe replay facade, DANDI NWB benchmark, Allen visual-coding benchmark and cross-dataset evidence summary. External API/export and vendor/user-upload examples remain handoff flows until real non-secret material is available.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v522_biosdk_public_examples.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Example Commands

```powershell
$env:PYTHONPATH='.'
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' examples/biosdk_v513_minimal_flow.py
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' examples/biosdk_v516_dandi_task_benchmark.py
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' examples/biosdk_v520_allen_orientation_benchmark.py
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' examples/biosdk_v521_cross_dataset_evidence.py
& 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe' examples/biosdk_v522_public_examples.py
```

## Outputs

- `outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json`
- `outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLE_CATALOG.json`
- `outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLE_CATALOG.csv`
- `outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLE_RUNBOOK.json`
- `outputs/v522_biosdk_public_examples/BIOGPU_V522_BIOSDK_PUBLIC_EXAMPLES_REPORT.md`

## Boundary

v5.22 makes the public evidence path easier to run and review. It does not claim full BioSDK, real external platform integration, vendor portability or BiC OS readiness.
