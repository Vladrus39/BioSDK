from __future__ import annotations

from pathlib import Path

from biogpu.sdk.external_review_finding_triage_v553 import run_external_review_finding_triage_workflow_v553, write_external_review_finding_triage_outputs_v553


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v553_external_review_finding_triage_example"
    audit = run_external_review_finding_triage_workflow_v553(root, out)
    write_external_review_finding_triage_outputs_v553(audit, out)
    print(audit["overall_status"])
    print(f"external_review_finding_triage_contract_ready={audit['external_review_finding_triage_contract_ready']}")
    print(f"local_finding_triage_ready_count={audit['local_finding_triage_ready_count']}")
    print(f"real_remediation_approval_count={audit['real_remediation_approval_count']}")
    print(f"review_finding_closed_count={audit['review_finding_closed_count']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()