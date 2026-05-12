#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile biogpu/integration/realdata_replay_v32.py biogpu/benchmarks/biogpu_v32_realdata_replay.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_biogpu_v32_realdata_replay.py
python -m biogpu.benchmarks.biogpu_v32_realdata_replay \
  --v15-dir outputs/realdata_zenodo_14363732_v15_readout \
  --out-dir outputs/realdata_zenodo_14363732_v32_realdata_e2e \
  --shuffle-count 20 \
  --seed 32
