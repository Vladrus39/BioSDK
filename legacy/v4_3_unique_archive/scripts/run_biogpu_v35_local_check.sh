#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile \
  biogpu/safety/boundary_v35.py \
  biogpu/safety/governance_v35.py \
  biogpu/release/release_hygiene_v35.py \
  biogpu/readout/linear_v27.py \
  biogpu/substrates/vendors/base_v25.py \
  biogpu/encoding/base_v26.py \
  biogpu/closed_loop/base_v28.py \
  biogpu/integration/e2e_v31.py \
  biogpu/integration/realdata_sweep_v33.py \
  biogpu/benchmarks/biogpu_v33_realdata_sweep.py \
  biogpu/benchmarks/biogpu_v35_release_hygiene.py
pytest -q tests/test_biogpu_v27_readout_layer.py tests/test_biogpu_v35_release_hygiene.py
python -m biogpu.benchmarks.biogpu_v35_release_hygiene --out-dir outputs/realdata_zenodo_14363732_v35_release_hygiene
