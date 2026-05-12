# BioGPU-Core v5.17 External Read-Only API Gate Guide

v5.17 validates the external read-only adapter contract without pretending that a real partner API has been proven.

The gate runs all local v3.7 mock clients, exports BioGPUTrace fixtures, verifies metadata/read-only trace availability, and confirms that write/live stimulation calls are denied. Real external proof remains blocked until a partner read-only token or vendor export is available.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v517_external_readonly_api_gate.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Outputs

- `outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_API_SUMMARY.json`
- `outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_PLATFORM_REPORTS.json`
- `outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_PLATFORM_REPORTS.csv`
- `outputs/v517_external_readonly_api_gate/V517_EXTERNAL_READONLY_TRACE_FIXTURES.json`
- `outputs/v517_external_readonly_api_gate/BIOGPU_V517_EXTERNAL_READONLY_API_REPORT.md`

## Boundary

This proves local adapter contract behavior only. It does not prove FinalSpark, 3Brain, Axion, MCS, or any other real partner API access. Store no secrets in outputs; only non-secret validation artifacts belong in the repository.
