#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m py_compile biogpu/metrics/energy_model_v29.py biogpu/metrics/latency_model_v29.py biogpu/metrics/baseline_v29.py biogpu/benchmarks/biogpu_v29_energy_performance.py
python -m pytest -q tests/test_biogpu_v29_energy_performance.py
python -m biogpu.benchmarks.biogpu_v29_energy_performance --out-dir outputs/realdata_zenodo_14363732_v29_energy
