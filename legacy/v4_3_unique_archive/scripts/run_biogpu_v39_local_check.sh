#!/usr/bin/env bash
set -euo pipefail
python -m py_compile biogpu/enterprise/licensing_v39.py biogpu/benchmarks/biogpu_v39_enterprise_package.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_biogpu_v39_enterprise_package.py
python -m biogpu.benchmarks.biogpu_v39_enterprise_package
