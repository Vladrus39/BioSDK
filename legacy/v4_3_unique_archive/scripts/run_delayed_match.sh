#!/usr/bin/env bash
set -euo pipefail
python -m biogpu.benchmarks.delayed_match --config configs/delayed_match.yaml
