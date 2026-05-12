#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
V15_DIR="${V15_DIR:-evidence/outputs/realdata_zenodo_14363732_v15_readout}"
OUT_DIR="${OUT_DIR:-outputs/powerpc_stage2_v36_lineage_compact}"
mkdir -p "$OUT_DIR"
python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap   --v15-dir "$V15_DIR"   --out-dir "$OUT_DIR"   --shuffle-count "${SHUFFLE_COUNT:-24}"   --bootstrap-iterations "${BOOTSTRAP_ITERATIONS:-500}"   --decoders "${DECODERS:-centroid_euclidean,diag_gaussian,logistic_l2,linear_svm}"   --ablations "${ABLATIONS:-response_delta_count,exact_features}"   --split-offsets "${SPLIT_OFFSETS:-0,1,2,3,4,5}"   --seed "${SEED:-36}"
