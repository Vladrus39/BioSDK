#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m py_compile $(find biogpu -name '*.py')
pytest -q tests/current
python -m biogpu.benchmarks.biogpu_v46_clean_release --project-root . --out-dir outputs/v46_clean_release
