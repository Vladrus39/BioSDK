"""Runner for BioGPU-Core v5.53 external review finding triage proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.external_review_finding_triage_v553 import DEFAULT_OUT, run_external_review_finding_triage_workflow_v553, write_external_review_finding_triage_outputs_v553


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_external_review_finding_triage_workflow_v553(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_external_review_finding_triage_outputs_v553(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.53 external review finding triage proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v553_external_review_finding_triage status={summary['overall_status']}")
    print(f"external_review_finding_triage_contract_ready={summary['external_review_finding_triage_contract_ready']}")
    print(f"v552_dependency_ready={summary['v552_dependency_ready']}")
    print(f"review_finding_triage_matrix_ready={summary['review_finding_triage_matrix_ready']}")
    print(f"remediation_plan_packet_ready={summary['remediation_plan_packet_ready']}")
    print(f"remediation_closure_gate_ready={summary['remediation_closure_gate_ready']}")
    print(f"real_remediation_approval_count={summary['real_remediation_approval_count']}")
    print(f"review_finding_closed_count={summary['review_finding_closed_count']}")
    print(f"real_external_review_ready={summary['real_external_review_ready']}")
    print(f"real_external_pilot_ready={summary['real_external_pilot_ready']}")
    print(f"production_ready={summary['production_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()