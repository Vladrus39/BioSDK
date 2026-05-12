# BioGPU-Core v5.24 External Export Validation Guide

v5.24 validates one small, non-secret, read-only external export file before the project treats external material as real evidence.

## Input

Place export files under one of these paths:

- `data/external/api_exports/<platform>/`
- `data/external/finalspark/`

Supported formats are JSON, CSV, HDF5, NWB and ZIP archives. ZIP files are listed but not treated as validated until a member file is extracted and validated directly.

## Current validated sample

The first validated sample is an official Multi Channel Systems McsPyDataTools test-data HDF5 fixture:

- Local path: `data/external/api_exports/mcs_mea2100/2014-07-09T10-17-35W8_Standard_all_500_Hz.h5`
- Size: `325330` bytes
- SHA256: `5d5bed4fbc745ab2bf9ed4d57b34ae6008fedee28b0f0c1855298182babb8852`
- Source family: MCS HDF5 RawData export fixture
- Validation: root attrs include `McsHdf5ProtocolType=RawData`, with analog/event/segment/timestamp datasets and no live-control safety hits.

## Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v524_external_export_validation.ps1 -Python "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe"
```

## Outputs

- `outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json`
- `outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_REPORTS.json`
- `outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_REPORTS.csv`
- `outputs/v524_external_export_validation/BIOGPU_V524_EXTERNAL_EXPORT_VALIDATION_REPORT.md`

The workflow also refreshes v5.17, v5.14, v5.21 and v5.22 outputs so downstream proof gates can see the validated read-only export.

## Boundary

This closes only the read-only external export blocker. It does not prove live API access, live stimulation, closed-loop control, production BioSDK, BioCompute Runtime or BiC OS readiness.
