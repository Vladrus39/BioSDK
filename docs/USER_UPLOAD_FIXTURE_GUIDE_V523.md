# BioGPU-Core v5.23 Safe User-Upload Fixture Guide

v5.23 closes the available user-upload blocker with a safe read-only JSON fixture.

The fixture is derived from local public evidence summaries and is placed under `data/external/user_upload_samples/`. It is meant to prove the user-upload scanner, hash, schema hint and importer routing path. It is not a vendor export and does not close the real external API/export blocker.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v523_user_upload_fixture.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Outputs

- `data/external/user_upload_samples/biosdk_v523_safe_user_fixture.json`
- `outputs/v523_user_upload_fixture/V523_USER_UPLOAD_FIXTURE_SUMMARY.json`
- `outputs/v523_user_upload_fixture/V523_USER_UPLOAD_FIXTURE_WORKFLOW.json`
- `outputs/v523_user_upload_fixture/BIOGPU_V523_USER_UPLOAD_FIXTURE_REPORT.md`

v5.23 also refreshes v5.19, v5.14, v5.21 and v5.22 outputs so the downstream proof matrix reflects the newly validated user-upload path.

## Boundary

This closes only the safe user-upload fixture path. Full BioSDK and BiC OS remain blocked by the real external read-only API/export proof.
