#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
mkdir -p outputs/v47_smoke
python -m pip check || true
python -m compileall -q biogpu
pytest -q tests/current
python -m biogpu.benchmarks.biogpu_v47_final_pc_patch --project-root . --out-dir outputs/v47_smoke > outputs/v47_smoke/v47_smoke_stdout.json
echo "v4.7 smoke OK: outputs/v47_smoke/v47_final_pc_patch_summary.json"

exit 0
