"""Runner for BioGPU-Core v5.55 closure signoff registry proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.closure_signoff_registry_v555 import DEFAULT_OUT, run_closure_signoff_registry_workflow_v555, write_closure_signoff_registry_outputs_v555


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_closure_signoff_registry_workflow_v555(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_closure_signoff_registry_outputs_v555(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.55 closure signoff registry proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v555_closure_signoff_registry status={summary['overall_status']}")
    print(f"closure_signoff_registry_contract_ready={summary['closure_signoff_registry_contract_ready']}")
    print(f"v554_dependency_ready={summary['v554_dependency_ready']}")
    print(f"signoff_registry_matrix_ready={summary['signoff_registry_matrix_ready']}")
    print(f"closure_signoff_audit_trail_ready={summary['closure_signoff_audit_trail_ready']}")
    print(f"external_reviewer_signoff_packet_ready={summary['external_reviewer_signoff_packet_ready']}")
    print(f"real_external_reviewer_signoff_ready_count={summary['real_external_reviewer_signoff_ready_count']}")
    print(f"real_closure_signoff_ready_count={summary['real_closure_signoff_ready_count']}")
    print(f"review_finding_closed_count={summary['review_finding_closed_count']}")
    print(f"production_distance={summary['production_distance_assessment']['distance']}")
    print(f"bic_os_distance={summary['bic_os_distance_assessment']['distance']}")
    print(f"production_ready={summary['production_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()