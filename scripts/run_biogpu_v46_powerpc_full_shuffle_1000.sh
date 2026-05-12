#!/usr/bin/env bash
set -euo pipefail
echo "Delegating legacy v4.6 wrapper to v4.7: scripts/run_biogpu_v47_powerpc_full_shuffle_1000.sh"
exec bash "$(dirname "$0")/run_biogpu_v47_powerpc_full_shuffle_1000.sh" "$@"
