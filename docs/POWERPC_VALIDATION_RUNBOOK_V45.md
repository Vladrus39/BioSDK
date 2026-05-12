# v4.5 Power-PC Validation Runbook

## Goal
Before broad beta claims, run the project on a workstation/server and produce paper-grade result bundles.

## Required runs
1. Re-run v3.5/v3.6 smoke checks.
2. Run `full_shuffle_1000` with lineage-strict splits.
3. Run `extended_methods_5000` if compute budget permits.
4. Run bootstrap confidence intervals.
5. Compare centroid, diag-gaussian, logistic regression, and linear SVM.
6. Produce global paper table: dataset/task/split/decoder/ablation/accuracy/balanced accuracy/shuffle mean/p-value/95% CI.
7. Mark negative findings honestly.

## Required data expansion
- Zenodo raw HDF5 / TTL reconstruction.
- DANDI/NWB task-aligned parser.
- AllenSDK visual coding/orientation benchmark.
- User-uploaded beta data import.

## Gate
The project may enter broader beta only after the power-PC result bundle is generated and reviewed.
