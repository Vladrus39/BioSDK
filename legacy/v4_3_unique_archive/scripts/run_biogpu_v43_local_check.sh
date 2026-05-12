#!/usr/bin/env bash
set -euo pipefail
python -m py_compile biogpu/beta/job_model_v43.py biogpu/api/hosted_server_v43.py biogpu/benchmarks/biogpu_v43_hosted_server.py
pytest -q tests/test_biogpu_v43_hosted_server.py
python -m biogpu.benchmarks.biogpu_v43_hosted_server
