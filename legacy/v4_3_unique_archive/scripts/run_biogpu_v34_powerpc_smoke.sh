#!/usr/bin/env bash
set -euo pipefail
python -m pytest -q tests/test_biogpu_v33_realdata_sweep.py tests/test_biogpu_v34_powerpc_runner.py
python -m biogpu.benchmarks.biogpu_v33_realdata_sweep --shuffle-count 2 --seed 3401 --out-dir outputs/powerpc_smoke_v34
python -m biogpu.benchmarks.biogpu_v34_powerpc_runner --out-dir outputs/realdata_zenodo_14363732_v34_powerpc
