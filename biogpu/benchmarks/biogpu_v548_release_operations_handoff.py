"""Runner for BioGPU-Core v5.48 release operations handoff proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.release_operations_handoff_v548 import DEFAULT_OUT, run_release_operations_handoff_workflow_v548, write_release_operations_handoff_outputs_v548


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_release_operations_handoff_workflow_v548(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_release_operations_handoff_outputs_v548(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.48 release operations handoff proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v548_release_operations_handoff status={summary['overall_status']}")
    print(f"release_operations_handoff_contract_ready={summary['release_operations_handoff_contract_ready']}")
    print(f"v547_dependency_ready={summary['v547_dependency_ready']}")
    print(f"release_operations_runbook_ready={summary['release_operations_runbook_ready']}")
    print(f"operator_handoff_matrix_ready={summary['operator_handoff_matrix_ready']}")
    print(f"operator_handoff_packet_ready={summary['operator_handoff_packet_ready']}")
    print(f"claim_boundary_attestation_ready={summary['claim_boundary_attestation_ready']}")
    print(f"production_release_ready={summary['production_release_ready']}")
    print(f"production_operations_ready={summary['production_operations_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()