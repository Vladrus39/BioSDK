#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
V15_DIR="${V15_DIR:-evidence/outputs/realdata_zenodo_14363732_v15_readout}"
OUT_DIR="${OUT_DIR:-outputs/powerpc_stage1_v33_compact}"
mkdir -p "$OUT_DIR"
python -m biogpu.benchmarks.biogpu_v33_realdata_sweep   --v15-dir "$V15_DIR"   --out-dir "$OUT_DIR"   --shuffle-count "${SHUFFLE_COUNT:-12}"   --seed "${SEED:-33}"   --decoders "${DECODERS:-centroid_euclidean,centroid_cosine,diag_gaussian,logistic_l2,linear_svm}"   --split-offsets "${SPLIT_OFFSETS:-0,1,2,3,4,5}"
