# BioGPU-Core compute backlog v1.7

Keep this file with the project. These are tasks that should be run on stronger hardware.

## CPU-heavy but required

1. v1.7 paper-full run:
   - negative counts: 1,3,5,10
   - at least 10 negative seeds
   - readouts: centroid, logistic_l2, linear_svm
   - feature sets: all, raw counts, no-rank/no-zscore, pulse-context control
   - 100 label shuffles

2. v1.7 final permutation run:
   - 20 negative seeds
   - 1000 label shuffles
   - raw-count-only and all-without-rank/zscore feature sets

3. Per-culture report:
   - fold-level AUC table
   - identify weak cultures/outliers
   - rerun excluding single-culture pathological cases only as sensitivity analysis, not as main result

## Data-heavy

1. Raw HDF5/TTL verification for Zenodo 14363732.
2. DANDI NWB task-aligned parser on a real downloaded dandiset.
3. Allen Brain Observatory orientation/tuning adapter.
4. External BRC reproduction target for arXiv 2602.05737 if code/data become available.

## Not needed for current v1.7

GPU is not required for logistic/SVM readouts. CPU and SSD matter more.
