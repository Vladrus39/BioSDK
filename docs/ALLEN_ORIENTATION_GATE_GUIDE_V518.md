# BioGPU-Core v5.18 Allen Orientation Gate Guide

v5.18 adds the next public-dataset proof gate for Allen visual-coding orientation samples.

The gate does not download the full Allen cache. It scans `data/external/allen/` for a small NWB file or Allen cache/session manifest, inspects local NWB files for units and orientation stimulus metadata, and records whether the project has enough evidence for the Allen orientation benchmark path.

## Run

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v518_allen_orientation_gate.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Download A Capped Allen Sample

Use the dedicated Allen helper instead of downloading the full Allen cache. It prefers a session-level NWB from DANDI `000021` and avoids the tiny per-probe LFP files that do not contain the full units/stimulus evidence needed for orientation validation.

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\download_allen_visual_coding_nwb_v518.ps1 -MaxMB 2048 -PlanOnly
& .\scripts\download_allen_visual_coding_nwb_v518.ps1 -MaxMB 2048
```

## Expected Current Status

Without a local Allen NWB/cache slice, the honest status is:

```text
allen_orientation_sample_missing_download_required
```

That status is useful: it keeps the BioSDK proof matrix accurate and prevents the project from treating synthetic orientation work as real Allen/public neurophysiology proof.

## Outputs

- `outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_GATE_SUMMARY.json`
- `outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_SAMPLE_REPORTS.json`
- `outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_ASSET_MANIFEST.csv`
- `outputs/v518_allen_orientation_gate/V518_ALLEN_ORIENTATION_DOWNLOAD_PLAN.json`
- `outputs/v518_allen_orientation_gate/BIOGPU_V518_ALLEN_ORIENTATION_GATE_REPORT.md`

## Boundary

v5.18 is an intake and validation gate unless a real Allen NWB/cache slice is present. It does not prove multi-dataset BioSDK readiness by itself, and it does not unlock BiC OS.
