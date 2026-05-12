#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile \
  biogpu/encoding/base_v26.py \
  biogpu/encoding/spatial_v26.py \
  biogpu/encoding/temporal_v26.py \
  biogpu/encoding/rate_v26.py \
  biogpu/encoding/hybrid_v26.py \
  biogpu/encoding/registry_v26.py \
  biogpu/benchmarks/biogpu_v26_encoder_layer.py
python -m biogpu.benchmarks.biogpu_v26_encoder_layer --out-dir outputs/realdata_zenodo_14363732_v26_encoder_layer
pytest -q tests/test_biogpu_v26_encoder_layer.py
