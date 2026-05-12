#!/usr/bin/env bash
set -euo pipefail
python -m py_compile biogpu/beta/access_policy_v41.py biogpu/benchmarks/biogpu_v41_access_audit.py
pytest -q tests/test_biogpu_v41_access_audit.py
python -m biogpu.benchmarks.biogpu_v41_access_audit --output outputs/realdata_zenodo_14363732_v41_access_audit
