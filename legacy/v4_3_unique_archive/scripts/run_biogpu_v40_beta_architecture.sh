#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m py_compile biogpu/beta/architecture_v40.py biogpu/api/beta_server_v40.py biogpu/benchmarks/biogpu_v40_beta_release_architecture.py
pytest -q tests/test_biogpu_v40_beta_release_architecture.py
python -m biogpu.benchmarks.biogpu_v40_beta_release_architecture --output outputs/realdata_zenodo_14363732_v40_beta_release
