#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/outputs/realdata_zenodo_14363732_v21_wetware"
mkdir -p "$OUT_DIR"
python -m biogpu.benchmarks.biogpu_v21_wetware_stack --out-dir "$OUT_DIR"
python -m pytest -q tests/test_biogpu_v21_wetware.py tests/test_biogpu_v21_wetware_session.py tests/test_biogpu_v21_registry.py
