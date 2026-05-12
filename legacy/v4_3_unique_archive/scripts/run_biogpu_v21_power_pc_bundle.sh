#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/outputs/realdata_zenodo_14363732_v21_wetware_powerpc"
mkdir -p "$OUT_DIR"
python -m biogpu.benchmarks.biogpu_v21_stack_analysis --out-dir "$OUT_DIR" --mode power_pc_full \
  --include-dir "$ROOT_DIR/outputs/realdata_zenodo_14363732_v17_paper_grade" \
  --include-dir "$ROOT_DIR/outputs/realdata_zenodo_14363732_v20_prototype"
echo "Bundle written under: $OUT_DIR"
