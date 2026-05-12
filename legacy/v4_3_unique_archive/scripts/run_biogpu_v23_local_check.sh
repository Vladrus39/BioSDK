#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUT_DIR="${1:-outputs/realdata_zenodo_14363732_v23_benchmark_registry}"

python -m compileall -q biogpu/benchmarks/registry_v23.py biogpu/benchmarks/biogpu_v23_benchmark_registry.py
python -m biogpu.benchmarks.biogpu_v23_benchmark_registry --out-dir "$OUT_DIR"

python - <<'PY'
from pathlib import Path
from biogpu.benchmarks.registry_v23 import build_biogpu_v23_benchmark_registry, validate_registry

registry = build_biogpu_v23_benchmark_registry()
errors = validate_registry(registry)
if errors:
    raise SystemExit("v2.3 registry validation failed: " + "; ".join(errors))

required = [
    Path("outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_benchmark_registry.json"),
    Path("outputs/realdata_zenodo_14363732_v23_benchmark_registry/BIOGPU_V23_BENCHMARK_REGISTRY.md"),
    Path("outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_benchmark_registry.csv"),
    Path("outputs/realdata_zenodo_14363732_v23_benchmark_registry/biogpu_v23_hardware_readiness_matrix.csv"),
]
for p in required:
    if not p.exists():
        raise SystemExit(f"missing output: {p}")
print("BioGPU v2.3 local check: OK")
PY
