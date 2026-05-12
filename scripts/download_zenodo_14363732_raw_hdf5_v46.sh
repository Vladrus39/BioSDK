#!/usr/bin/env bash
set -euo pipefail
echo "Delegating legacy v4.6 wrapper to v4.7: scripts/download_zenodo_14363732_raw_hdf5_v47.sh"
exec bash "$(dirname "$0")/download_zenodo_14363732_raw_hdf5_v47.sh" "$@"
