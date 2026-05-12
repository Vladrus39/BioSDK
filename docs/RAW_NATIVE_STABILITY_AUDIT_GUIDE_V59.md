# BioGPU-Core v5.9 Raw-Native Stability Audit Guide

## Purpose

v5.9 audits the raw-native feature matrix created in v5.8. It asks two stricter questions:

- Are raw event-window features internally repeatable within each recording?
- Is there enough repeated target coverage to support target-ID readout claims?

## Inputs

The default inputs are v5.8 outputs:

- `outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_MATRIX.npz`
- `outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_EVENT_METADATA.csv`

## Outputs

The runner writes these artifacts under `outputs/v59_raw_native_stability_audit/`:

- `V59_RAW_NATIVE_STABILITY_SUMMARY.json`
- `V59_RAW_NATIVE_TARGET_ELIGIBILITY.csv`
- `V59_RAW_NATIVE_SPLIT_HALF_REPEATABILITY.json`
- `V59_RAW_NATIVE_SPLIT_HALF_BY_RECORDING.csv`
- `V59_RAW_NATIVE_TARGET_READOUT.json`
- `V59_RAW_NATIVE_TARGET_FINGERPRINT.json`
- `BIOGPU_V59_RAW_NATIVE_STABILITY_AUDIT_REPORT.md`

## Interpretation

High split-half repeatability supports the raw feature extraction pipeline: events from the same raw recording produce stable event-window fingerprints.

Target-ID readout is stricter. v5.9 only includes targets with repeated raw recordings in group-heldout target tests. Single-recording targets are reported as coverage gaps, not silently used as evidence.

## Validation

Run the v5.9 gate on Windows:

```powershell
& .\scripts\run_biogpu_v59_raw_native_stability_audit.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The default run uses 200 label shuffles. It analyzes existing v5.8 artifacts and only regenerates v5.8 outputs if they are missing.

## Claim Boundary

v5.9 is a raw-native event-window stability and target coverage audit. It does not prove live biology, GPU replacement, energy superiority or v15/v50 raw equivalence.
