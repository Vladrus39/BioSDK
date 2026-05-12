#!/usr/bin/env bash
set -euo pipefail
python -m py_compile biogpu/apis/base_external_api_v37.py biogpu/benchmarks/biogpu_v37_external_api_integration.py
pytest -q tests/test_biogpu_v37_external_api.py
python -m biogpu.benchmarks.biogpu_v37_external_api_integration
