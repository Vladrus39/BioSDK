#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m compileall -q biogpu
pytest -q tests/current/test_biogpu_v48_product_identity.py
python -m biogpu.benchmarks.biogpu_v48_product_identity --help >/dev/null 2>&1 || true
python -m biogpu.benchmarks.biogpu_v48_product_identity
