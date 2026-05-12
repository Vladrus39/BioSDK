#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m biogpu.benchmarks.biogpu_v18_runtime_analysis \
  outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v18_biogpu_core \
  --demo-jobs 8 \
  --seed 18
python -m py_compile \
  biogpu/runtime/contracts.py \
  biogpu/runtime/replay_runtime.py \
  biogpu/benchmarks/biogpu_v18_runtime_analysis.py
printf '\nBioGPU v1.8 local check complete.\n'
