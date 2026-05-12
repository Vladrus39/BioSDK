#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile biogpu/closed_loop/base_v28.py biogpu/closed_loop/policy_v28.py biogpu/closed_loop/reward_v28.py biogpu/closed_loop/controller_v28.py biogpu/closed_loop/registry_v28.py biogpu/benchmarks/biogpu_v28_closed_loop_controller.py
python -m pytest -q tests/test_biogpu_v28_closed_loop_controller.py
python -m biogpu.benchmarks.biogpu_v28_closed_loop_controller --out-dir outputs/realdata_zenodo_14363732_v28_closed_loop
