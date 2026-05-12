#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/outputs/realdata_zenodo_14363732_v22_hardware"
mkdir -p "$OUT_DIR"
python -m biogpu.benchmarks.biogpu_v22_hardware_blueprint --out-dir "$OUT_DIR"
python -m pytest -q tests/test_biogpu_v22_hardware_blueprint.py
