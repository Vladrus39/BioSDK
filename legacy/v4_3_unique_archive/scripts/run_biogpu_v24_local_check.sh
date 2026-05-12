#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/outputs/realdata_zenodo_14363732_v24_session_manager"

python -m biogpu.benchmarks.biogpu_v24_session_manager \
  --out-dir "$OUT_DIR" \
  --run-mode dry_run \
  --hardware-profile software_only \
  --operator-note "v2.4 local dry run"

python -m pytest -q tests/test_biogpu_v24_session_manager.py
