#!/usr/bin/env bash
set -euo pipefail
python -m py_compile \
  biogpu/statistics/lineage_split_v36.py \
  biogpu/statistics/bootstrap_v36.py \
  biogpu/benchmarks/biogpu_v36_lineage_bootstrap.py
pytest -q tests/test_biogpu_v36_lineage_bootstrap.py
python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap \
  --v15-dir outputs/realdata_zenodo_14363732_v15_readout \
  --out-dir outputs/realdata_zenodo_14363732_v36_lineage_bootstrap \
  --shuffle-count 3 \
  --bootstrap-iterations 100 \
  --decoders centroid_euclidean,diag_gaussian \
  --ablations response_delta_count \
  --split-offsets 0,1,2
