#!/usr/bin/env bash
set -euo pipefail
python -m py_compile biogpu/datasets/registry_v42.py biogpu/datasets/importers_v42.py biogpu/benchmarks/biogpu_v42_dataset_registry.py
pytest -q tests/test_biogpu_v42_dataset_registry.py
python -m biogpu.benchmarks.biogpu_v42_dataset_registry
