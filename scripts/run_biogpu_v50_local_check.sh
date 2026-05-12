#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m compileall -q biogpu
python -m pytest -q tests/current/test_biogpu_v50_differentiation.py
python -m biogpu.benchmarks.biogpu_v50_differentiation_roadmap
