# BioGPU-Core v5.14 Sample Acquisition Guide

v5.14 keeps the project on the BioSDK proof path. It inventories local samples, marks missing evidence sources, and produces a selective download plan for real external samples.

The goal is not to download every public archive. The goal is to add enough diverse, inspectable samples to prove the SDK path honestly.

## Current Sample Targets

- `zenodo_14363732_preprocessed`: already used for PC validation evidence.
- `zenodo_14363732_raw_hdf5`: already downloaded/extracted locally and used for raw HDF5 gates, with remaining raw-equivalence and target-ID limits.
- `dandi_nwb_task_sample`: next required public NWB sample.
- `allen_visual_coding_orientation_sample`: later external orientation benchmark sample.
- `external_readonly_api_or_export_sample`: partner/vendor read-only trace/export, with no live actuation.
- `vendor_or_user_upload_sample`: private beta and portability sample.

## Run The Gate

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\run_biogpu_v514_sample_acquisition_gate.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

## Plan A DANDI NWB Download

```powershell
Push-Location 'C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap'
& .\scripts\download_dandi_nwb_sample_v514.ps1 -DandisetId 000469 -MaxMB 512 -PlanOnly
```

If the plan finds a suitable asset under the cap, run the same command without `-PlanOnly`.

## Why Capped Downloads

Full public neuroscience archives can be very large. v5.14 defaults to one capped, traceable NWB asset first. After that sample validates, the SDK examples can expand to more assets and datasets.

## Claim Boundary

This gate supports BioSDK sample acquisition and proof planning. It does not claim full BioSDK, production runtime, live BioGPU, or BiC OS readiness.
