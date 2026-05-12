from __future__ import annotations

from pathlib import Path

from biogpu.sdk.remediation_evidence_closure_v554 import run_remediation_evidence_closure_workflow_v554, write_remediation_evidence_closure_outputs_v554


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v554_remediation_evidence_closure_example"
    audit = run_remediation_evidence_closure_workflow_v554(root, out)
    write_remediation_evidence_closure_outputs_v554(audit, out)
    print(audit["overall_status"])
    print(f"remediation_evidence_closure_contract_ready={audit['remediation_evidence_closure_contract_ready']}")
    print(f"local_remediation_evidence_verified_count={audit['local_remediation_evidence_verified_count']}")
    print(f"real_closure_attestation_ready_count={audit['real_closure_attestation_ready_count']}")
    print(f"real_external_review_ready={audit['real_external_review_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()