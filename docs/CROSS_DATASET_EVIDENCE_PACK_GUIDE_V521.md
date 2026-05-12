# BioGPU-Core v5.21 Cross-Dataset Evidence Pack Guide

v5.21 aggregates the current proof layer into one BioSDK-level report.

It reads local summaries from Zenodo raw HDF5, DANDI NWB, Allen visual coding, external read-only API/export, vendor/user-upload intake and the v5.14 sample matrix. It does not download new data.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v521_cross_dataset_evidence_pack.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Outputs

- `outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json`
- `outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_SOURCE_MATRIX.json`
- `outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_SOURCE_MATRIX.csv`
- `outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_BLOCKER_MATRIX.json`
- `outputs/v521_cross_dataset_evidence_pack/BIOGPU_V521_CROSS_DATASET_EVIDENCE_REPORT.md`

## Boundary

v5.21 can say that the public cross-dataset evidence layer is ready when Zenodo raw HDF5, DANDI NWB and Allen visual-coding benchmarks are present. It still cannot claim full BioSDK or BiC OS readiness until real external API/export and vendor/user-upload blockers are closed.
