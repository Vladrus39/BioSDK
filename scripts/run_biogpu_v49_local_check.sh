#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m compileall -q biogpu
pytest -q tests/current/test_biogpu_v49_naming_os_strategy.py
python -m biogpu.benchmarks.biogpu_v49_naming_os_strategy
