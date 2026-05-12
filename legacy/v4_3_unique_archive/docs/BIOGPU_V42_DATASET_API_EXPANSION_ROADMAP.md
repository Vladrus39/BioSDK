# BioGPU v4.2 Dataset/API Expansion Roadmap

## P0 — must finish before credible private beta

1. Reproduce v3.5/v3.6 smoke on workstation.
2. Download and inspect Zenodo raw HDF5.
3. Reconstruct TTL/protocol windows where possible.
4. Validate raw-derived windows against preprocessed features.
5. Run lineage-strict full_shuffle_1000.
6. Generate bootstrap confidence intervals.

## P1 — needed before enterprise pilot

1. DANDI discovery: find 3–5 NWB datasets with `units` and `intervals/trials/stimulus`.
2. AllenSDK orientation-like benchmark.
3. FinalSpark read-only/export credential test.
4. User upload importer for CSV/NWB/HDF5.
5. Hosted server upload validation and schema preview.

## P2 — vendor portability

1. Collect sample exports from MCS, 3Brain, and Axion.
2. Implement schema inference and channel mapping.
3. Normalize vendor traces into BioGPUTrace.
4. Compare cross-vendor readout behavior.

## P3 — future lab-approved module

1. Live-shadow beside approved lab experiment.
2. Operator-supervised closed-loop dry-run.
3. Allowlisted command schema.
4. Lab-approved live BioGPU experiment.
