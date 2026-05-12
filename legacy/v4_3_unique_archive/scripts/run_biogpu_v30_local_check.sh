#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
OUT_DIR="$ROOT_DIR/outputs/realdata_zenodo_14363732_v30_whitepaper"
mkdir -p "$OUT_DIR"
python -m py_compile biogpu/paper/package_v30.py biogpu/benchmarks/biogpu_v30_whitepaper_package.py
python -m biogpu.benchmarks.biogpu_v30_whitepaper_package --out-dir "$OUT_DIR" --write-root
pytest -q tests/test_biogpu_v30_whitepaper_package.py
