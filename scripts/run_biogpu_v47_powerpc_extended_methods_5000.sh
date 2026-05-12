#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
V15_DIR="${V15_DIR:-evidence/outputs/realdata_zenodo_14363732_v15_readout}"
OUT_DIR="${OUT_DIR:-outputs/powerpc_extended_methods_5000}"
mkdir -p "$OUT_DIR"
cat > "$OUT_DIR/RUN_MANIFEST_EXTENDED_METHODS_5000.txt" <<EOF
BioGPU v4.7 extended_methods_5000 run
This is intentionally heavy. Run only after full_shuffle_1000 completes and results are stable.
V15_DIR=$V15_DIR
OUT_DIR=$OUT_DIR
EOF
python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap   --v15-dir "$V15_DIR"   --out-dir "$OUT_DIR/lineage_v36_extended"   --shuffle-count "${SHUFFLE_COUNT:-5000}"   --bootstrap-iterations "${BOOTSTRAP_ITERATIONS:-5000}"   --decoders "${DECODERS:-centroid_euclidean,centroid_cosine,diag_gaussian,logistic_l2,linear_svm}"   --ablations "${ABLATIONS:-all_features,response_delta_count,response_count,pre_response_count,exact_features}"   --split-offsets "${SPLIT_OFFSETS:-0,1,2,3,4,5,6,7,8,9}"   --seed "${SEED:-4750}"
