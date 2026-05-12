# BioGPU-Core v5.6 Raw HDF5 Structure Guide

## Purpose

v5.6 maps the downloaded Zenodo 14363732 raw HDF5 archive without loading full waveform matrices into memory.

The goal is to turn the raw archive into auditable structure evidence:

- HDF5 file count and byte size;
- MCS RawData protocol metadata;
- analog stream path, channel count, sample count and inferred sample rate;
- event stream and event-entity candidates;
- first-pass stimulus-window previews for downstream reconstruction.

## Safety boundary

This phase is offline read-only inspection. It does not perform live biology, stimulation, vendor writes or wet-lab control.

## Outputs

The runner writes these artifacts under `outputs/v56_raw_hdf5_structure/`:

- `V56_RAW_HDF5_STRUCTURE_SUMMARY.json`
- `V56_RAW_HDF5_FILE_REPORT.json`
- `V56_TTL_EVENT_CANDIDATES.csv`
- `V56_RAW_STIMULUS_WINDOWS_PREVIEW.csv`
- `BIOGPU_V56_RAW_HDF5_STRUCTURE_REPORT.md`

## Validation

Run the v5.6 gate on Windows:

```powershell
& .\scripts\run_biogpu_v56_raw_hdf5_structure.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The gate inspects the downloaded raw HDF5 files and then runs focused tests against a small synthetic MCS-style HDF5 fixture.
