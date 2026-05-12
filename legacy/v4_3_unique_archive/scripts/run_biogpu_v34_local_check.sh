#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile biogpu/powerpc/runner_plan_v34.py biogpu/benchmarks/biogpu_v34_powerpc_runner.py
python -m pytest -q tests/test_biogpu_v34_powerpc_runner.py
python -m biogpu.benchmarks.biogpu_v34_powerpc_runner --out-dir outputs/realdata_zenodo_14363732_v34_powerpc
