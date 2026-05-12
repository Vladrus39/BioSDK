#!/usr/bin/env bash
set -euo pipefail
bash scripts/run_biogpu_v35_local_check.sh
python -m biogpu.benchmarks.biogpu_v33_realdata_sweep \
  --shuffle-count 2 \
  --seed 3501 \
  --split-offsets 0,1 \
  --decoders centroid_euclidean,logistic_l2,linear_svm \
  --out-dir outputs/powerpc_smoke_v35
