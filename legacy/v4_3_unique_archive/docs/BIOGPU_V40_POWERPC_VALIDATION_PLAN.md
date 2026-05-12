# BioGPU v4.0 Power-PC Validation Plan

Before private beta, power-PC validation must run larger statistics than this environment can handle.

## Required runs

- full_shuffle_1000
- extended_methods_5000 where feasible
- lineage-strict splits
- bootstrap confidence intervals
- feature ablations
- decoder comparison
- calibration/negative controls
- raw-vs-preprocessed comparison after raw HDF5 ingestion

## Output table

Every dataset/task must produce:

- dataset id
- task id
- split policy
- decoder
- ablation
- accuracy / balanced accuracy
- shuffle mean
- empirical p-value
- 95% CI
- claim level
