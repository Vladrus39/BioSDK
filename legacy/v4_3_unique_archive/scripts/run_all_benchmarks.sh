#!/usr/bin/env bash
set -euo pipefail
python -m biogpu.benchmarks.orientation --config configs/orientation.yaml
python -m biogpu.benchmarks.noise --config configs/noise.yaml
python -m biogpu.benchmarks.sequence --config configs/sequence.yaml
python -m biogpu.benchmarks.delayed_match --config configs/delayed_match.yaml
python -m biogpu.benchmarks.ablation --config configs/ablation.yaml
python -m biogpu.dashboard.generate_static

python -m biogpu.benchmarks.streaming --config configs/streaming.yaml
python -m biogpu.dashboard.generate_static
