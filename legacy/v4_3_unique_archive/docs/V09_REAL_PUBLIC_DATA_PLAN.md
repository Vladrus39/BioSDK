# v0.9 Real Public Data Plan

v0.9 turns the public-data path into a concrete workflow.

## What changed

- Zenodo 14363732 manifest is embedded in code.
- Direct download script targets the small preprocessed spike zip first.
- NWB discovery can inspect local NWB/HDF5 files for `/units`, `/intervals`, and `/stimulus` candidates.
- BRC 2602.05737 is represented as a reproducibility contract, not as a fabricated dataset.
- Public data status report can be generated without internet access.

## Correct workflow

1. Download Zenodo `Pre_processed_MEA_data.zip`.
2. Extract TXT spike files.
3. Run `zenodo-profile` to verify real spikes enter the BioGPU pipeline.
4. For task claims, create `stimulus_windows.csv` from real experiment metadata.
5. Use DANDI/NWB datasets only after mapping real task intervals into `start_s,end_s,label` windows.

## Honesty rule

Spike times alone are not enough for classification claims. A valid benchmark requires real stimulus/behavior windows.
