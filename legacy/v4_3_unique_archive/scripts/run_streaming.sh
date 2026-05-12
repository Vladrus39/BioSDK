#!/usr/bin/env bash
set -euo pipefail
python -m biogpu.benchmarks.streaming --config configs/streaming.yaml
