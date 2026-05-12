# BioGPU-Core v5.7 Raw vs Preprocessed Alignment Guide

## Purpose

v5.7 audits whether the raw HDF5 EventStream candidates mapped in v5.6 cover the exact preprocessed pulse-window recordings used by the v15/v50 PC validation path.

The goal is conservative evidence accounting:

- group raw HDF5 event candidates by date, culture, condition, target and recording stem;
- group v15 pulse metadata by the same recording-level keys;
- report exact recording overlap separately from weaker condition/target and temporal-signature overlap;
- prevent raw reconstruction claims when the current local raw and preprocessed subsets do not cover the same recordings.

## Safety boundary

This phase is offline, read-only and audit-only. It does not load full waveform matrices, perform live biology, control hardware or claim raw feature reconstruction.

## Outputs

The runner writes these artifacts under `outputs/v57_raw_preprocessed_alignment/`:

- `V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json`
- `V57_RAW_EVENT_RECORDINGS.csv`
- `V57_PREPROCESSED_PULSE_RECORDINGS.csv`
- `V57_RAW_PREPROCESSED_ALIGNMENT_AUDIT.csv`
- `BIOGPU_V57_RAW_PREPROCESSED_ALIGNMENT_REPORT.md`

## Interpretation

`exact_recording_alignment_available` means at least one raw event recording shares date, culture, condition, target and recording stem with a preprocessed pulse recording.

`target_and_temporal_signature_only` or `class_temporal_signature_only` means the raw and preprocessed datasets share target/cadence evidence, but not exact recording-level coverage. That is useful for dataset understanding, but it is not enough to claim raw-to-feature reconstruction for the PC validation rows.

## Validation

Run the v5.7 gate on Windows:

```powershell
& .\scripts\run_biogpu_v57_raw_preprocessed_alignment.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The gate reuses `outputs/v56_raw_hdf5_structure/V56_TTL_EVENT_CANDIDATES.csv`, reads `evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv`, writes the v5.7 audit artifacts and runs focused tests.
