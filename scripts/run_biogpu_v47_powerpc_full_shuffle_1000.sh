#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
V15_DIR="${V15_DIR:-evidence/outputs/realdata_zenodo_14363732_v15_readout}"
OUT_DIR="${OUT_DIR:-outputs/powerpc_full_shuffle_1000}"
mkdir -p "$OUT_DIR"
cat > "$OUT_DIR/RUN_MANIFEST_FULL_SHUFFLE_1000.txt" <<EOF
BioGPU v4.7 full_shuffle_1000 run
V15_DIR=$V15_DIR
OUT_DIR=$OUT_DIR
DECODERS=${DECODERS:-centroid_euclidean,diag_gaussian,logistic_l2,linear_svm}
ABLATIONS=${ABLATIONS:-response_delta_count,exact_features}
SPLIT_OFFSETS=${SPLIT_OFFSETS:-0,1,2,3,4,5}
SHUFFLE_COUNT=${SHUFFLE_COUNT:-1000}
BOOTSTRAP_ITERATIONS=${BOOTSTRAP_ITERATIONS:-2000}
EOF
python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap   --v15-dir "$V15_DIR"   --out-dir "$OUT_DIR"   --shuffle-count "${SHUFFLE_COUNT:-1000}"   --bootstrap-iterations "${BOOTSTRAP_ITERATIONS:-2000}"   --decoders "${DECODERS:-centroid_euclidean,diag_gaussian,logistic_l2,linear_svm}"   --ablations "${ABLATIONS:-response_delta_count,exact_features}"   --split-offsets "${SPLIT_OFFSETS:-0,1,2,3,4,5}"   --seed "${SEED:-4700}"
