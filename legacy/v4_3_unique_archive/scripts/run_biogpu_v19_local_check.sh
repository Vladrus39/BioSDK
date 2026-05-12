#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m biogpu.benchmarks.biogpu_v19_engineering_analysis \
  --v15-out outputs/realdata_zenodo_14363732_v15_readout \
  --out outputs/realdata_zenodo_14363732_v19_engineering \
  --image outputs/realdata_zenodo_14363732_v19_engineering/biogpu_material_visualization.png \
  --closed-loop-steps 8 \
  --seed 19
