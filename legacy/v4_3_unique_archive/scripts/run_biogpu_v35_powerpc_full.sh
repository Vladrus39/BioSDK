#!/usr/bin/env bash
set -euo pipefail
# Full v3.5 power-PC target: v3.4 full sweep plus real sklearn decoders.
for seed in 35001 35002 35003; do
  python -m biogpu.benchmarks.biogpu_v33_realdata_sweep \
    --shuffle-count 1000 \
    --seed "$seed" \
    --split-offsets 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17 \
    --decoders centroid_euclidean,centroid_cosine,diag_gaussian,logistic_l2,linear_svm \
    --out-dir "outputs/powerpc_full_v35_seed_${seed}"
done
