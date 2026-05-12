#!/usr/bin/env bash
set -euo pipefail
DATASET_ZIP=${1:-data/external/Pre_processed_MEA_data.zip}
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m biogpu.benchmarks.biogpu_v46_clean_release --project-root . --dataset-zip "$DATASET_ZIP" --out-dir outputs/v46_clean_release_asset_validation
