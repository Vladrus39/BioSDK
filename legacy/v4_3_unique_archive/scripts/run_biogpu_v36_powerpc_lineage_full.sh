#!/usr/bin/env bash
set -euo pipefail
python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap \
  --v15-dir outputs/realdata_zenodo_14363732_v15_readout \
  --out-dir outputs/realdata_zenodo_14363732_v36_lineage_bootstrap_full \
  --shuffle-count 1000 \
  --bootstrap-iterations 5000 \
  --decoders centroid_euclidean,centroid_cosine,diag_gaussian,logistic_l2,linear_svm \
  --ablations all_features,response_delta_count,response_count,pre_response_count,exact_features \
  --split-offsets 0,1,2,3,4,5,6,7,8,9
