#!/usr/bin/env bash
set -euo pipefail
echo "Delegating legacy v4.6 wrapper to v4.7: scripts/run_biogpu_v47_powerpc_stage2_v36_lineage_compact.sh"
exec bash "$(dirname "$0")/run_biogpu_v47_powerpc_stage2_v36_lineage_compact.sh" "$@"
