#!/usr/bin/env bash
set -euo pipefail
python -m biogpu.benchmarks.ablation --config configs/ablation.yaml
