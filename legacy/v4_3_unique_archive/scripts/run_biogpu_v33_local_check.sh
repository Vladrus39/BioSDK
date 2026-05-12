#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile biogpu/integration/realdata_sweep_v33.py biogpu/benchmarks/biogpu_v33_realdata_sweep.py
python -m biogpu.benchmarks.biogpu_v33_realdata_sweep \
  --v15-dir outputs/realdata_zenodo_14363732_v15_readout \
  --out-dir outputs/realdata_zenodo_14363732_v33_paper_sweep \
  --shuffle-count 12 \
  --seed 33
python -m pytest -q tests/test_biogpu_v33_realdata_sweep.py
