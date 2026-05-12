#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
OUT_DIR="outputs/realdata_zenodo_14363732_v25_vendor_adapters"
python -m biogpu.benchmarks.biogpu_v25_vendor_adapters --out-dir "$OUT_DIR"
python -m pytest -q tests/test_biogpu_v25_vendor_adapters.py
