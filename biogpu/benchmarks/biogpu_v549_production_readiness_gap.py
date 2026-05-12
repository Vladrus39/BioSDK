"""Runner for BioGPU-Core v5.49 production readiness gap proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.production_readiness_gap_v549 import DEFAULT_OUT, run_production_readiness_gap_workflow_v549, write_production_readiness_gap_outputs_v549


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_production_readiness_gap_workflow_v549(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_production_readiness_gap_outputs_v549(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.49 production readiness gap proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v549_production_readiness_gap status={summary['overall_status']}")
    print(f"production_readiness_gap_contract_ready={summary['production_readiness_gap_contract_ready']}")
    print(f"v548_dependency_ready={summary['v548_dependency_ready']}")
    print(f"production_readiness_gap_matrix_ready={summary['production_readiness_gap_matrix_ready']}")
    print(f"staged_pilot_acceptance_matrix_ready={summary['staged_pilot_acceptance_matrix_ready']}")
    print(f"readiness_blocker_register_ready={summary['readiness_blocker_register_ready']}")
    print(f"open_gap_count={summary['open_gap_count']}")
    print(f"production_ready_domain_count={summary['production_ready_domain_count']}")
    print(f"production_ready={summary['production_ready']}")
    print(f"real_external_pilot_ready={summary['real_external_pilot_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()