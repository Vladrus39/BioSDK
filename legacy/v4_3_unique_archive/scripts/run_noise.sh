#!/usr/bin/env bash
set -euo pipefail
python -m biogpu.benchmarks.noise --config configs/noise.yaml
