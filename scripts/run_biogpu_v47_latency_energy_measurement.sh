#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
OUT_DIR="${OUT_DIR:-outputs/powerpc_latency_energy}"
V15_DIR="${V15_DIR:-evidence/outputs/realdata_zenodo_14363732_v15_readout}"
mkdir -p "$OUT_DIR"
START=$(date +%s)
python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap   --v15-dir "$V15_DIR"   --out-dir "$OUT_DIR/fixed_latency_run"   --shuffle-count "${SHUFFLE_COUNT:-12}"   --bootstrap-iterations "${BOOTSTRAP_ITERATIONS:-100}"   --decoders "${DECODERS:-diag_gaussian,logistic_l2,linear_svm}"   --ablations "${ABLATIONS:-response_delta_count}"   --split-offsets "${SPLIT_OFFSETS:-0,1,2}"   --seed "${SEED:-4790}"
END=$(date +%s)
cat > "$OUT_DIR/latency_energy_measurement_report.md" <<EOF
# BioGPU v4.7 Latency / Energy Measurement Report

Wall clock seconds: $((END-START))

Power measurement is host-specific. Add external meter / nvidia-smi / powertop / RAPL logs here if available.

Recommended attachments:
- CPU model and RAM
- GPU model if used
- wall power meter log
- nvidia-smi dmon log where applicable
- raw command stdout/stderr
EOF
