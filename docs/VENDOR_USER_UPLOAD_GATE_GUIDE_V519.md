# BioGPU-Core v5.19 Vendor/User Upload Gate Guide

v5.19 adds a read-only intake gate for vendor exports and user-uploaded sample fixtures.

It scans `data/external/vendor_exports/` and `data/external/user_upload_samples/`, computes SHA256 hashes, detects basic schema hints, routes samples through the existing v4.2 import skeletons, and blocks files that contain live stimulation, pinout, wiring or wet-lab recipe fields.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v519_vendor_user_upload_gate.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Expected Current Status

Without local vendor/user sample files, the honest status is:

```text
vendor_user_upload_sample_missing_required
```

That keeps the project honest: vendor portability and private beta upload proof need at least one safe read-only sample file.

## Accepted Local Paths

- `data/external/vendor_exports/`
- `data/external/user_upload_samples/`

Accepted extensions: `csv`, `json`, `nwb`, `h5`, `hdf5`, `zip`.

## Outputs

- `outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json`
- `outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_SAMPLE_REPORTS.json`
- `outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_SAMPLE_REPORTS.csv`
- `outputs/v519_vendor_user_upload_gate/V519_VENDOR_USER_UPLOAD_INTAKE_TEMPLATE.json`
- `outputs/v519_vendor_user_upload_gate/BIOGPU_V519_VENDOR_USER_UPLOAD_GATE_REPORT.md`

## Boundary

This is read-only intake validation. It is not a live vendor adapter, not a closed-loop control path, and not BiC OS readiness.
