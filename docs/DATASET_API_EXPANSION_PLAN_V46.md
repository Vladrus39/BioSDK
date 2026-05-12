# BioGPU v4.6 Dataset/API Expansion Plan

## Baseline already registered

- Zenodo 14363732 preprocessed MEA archive

## Must add on powerful PC/server

1. Zenodo raw HDF5 / TTL / stimulus reconstruction.
2. DANDI/NWB discovery and task-aligned parser.
3. AllenSDK visual coding/orientation benchmark.
4. FinalSpark read-only/export validation when access is available.
5. MCS/3Brain/Axion vendor export validation.
6. User-uploaded private neural data importer for beta testers.

## Acceptance criteria

Each dataset adapter must produce:

- dataset profile
- import manifest
- task/window table where applicable
- feature matrix or trace export
- benchmark result bundle
- audit log
- known limitations
