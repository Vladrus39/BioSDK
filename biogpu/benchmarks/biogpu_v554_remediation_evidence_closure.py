"""Runner for BioGPU-Core v5.54 remediation evidence closure proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.remediation_evidence_closure_v554 import DEFAULT_OUT, run_remediation_evidence_closure_workflow_v554, write_remediation_evidence_closure_outputs_v554


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_remediation_evidence_closure_workflow_v554(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_remediation_evidence_closure_outputs_v554(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.54 remediation evidence closure proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v554_remediation_evidence_closure status={summary['overall_status']}")
    print(f"remediation_evidence_closure_contract_ready={summary['remediation_evidence_closure_contract_ready']}")
    print(f"v553_dependency_ready={summary['v553_dependency_ready']}")
    print(f"remediation_evidence_matrix_ready={summary['remediation_evidence_matrix_ready']}")
    print(f"closure_attestation_packet_ready={summary['closure_attestation_packet_ready']}")
    print(f"closure_attestation_gate_ready={summary['closure_attestation_gate_ready']}")
    print(f"real_closure_attestation_ready_count={summary['real_closure_attestation_ready_count']}")
    print(f"finding_closure_attested_count={summary['finding_closure_attested_count']}")
    print(f"real_external_review_ready={summary['real_external_review_ready']}")
    print(f"real_external_pilot_ready={summary['real_external_pilot_ready']}")
    print(f"production_ready={summary['production_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()