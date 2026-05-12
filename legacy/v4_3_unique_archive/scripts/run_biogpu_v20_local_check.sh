#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/outputs/realdata_zenodo_14363732_v20_prototype"
IMG_PATH="$ROOT_DIR/outputs/realdata_zenodo_14363732_v19_engineering/biogpu_material_visualization.png"
mkdir -p "$OUT_DIR"
python -m biogpu.benchmarks.biogpu_v20_prototype_analysis --out-dir "$OUT_DIR" --image-path "$IMG_PATH"
python -m pytest -q tests/test_biogpu_v20_prototype.py
