#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile biogpu/readout/base_v27.py biogpu/readout/centroid_v27.py biogpu/readout/linear_v27.py biogpu/readout/online_v27.py biogpu/readout/registry_v27.py biogpu/benchmarks/biogpu_v27_readout_layer.py
python -m pytest -q tests/test_biogpu_v27_readout_layer.py
python -m biogpu.benchmarks.biogpu_v27_readout_layer --out-dir outputs/realdata_zenodo_14363732_v27_readout_layer
