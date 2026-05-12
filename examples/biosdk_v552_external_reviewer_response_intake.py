from __future__ import annotations

from pathlib import Path

from biogpu.sdk.external_reviewer_response_intake_v552 import run_external_reviewer_response_intake_workflow_v552, write_external_reviewer_response_intake_outputs_v552


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v552_external_reviewer_response_intake_example"
    audit = run_external_reviewer_response_intake_workflow_v552(root, out)
    write_external_reviewer_response_intake_outputs_v552(audit, out)
    print(audit["overall_status"])
    print(f"external_reviewer_response_intake_contract_ready={audit['external_reviewer_response_intake_contract_ready']}")
    print(f"local_questionnaire_score_ready_count={audit['local_questionnaire_score_ready_count']}")
    print(f"signed_review_response_ready_count={audit['signed_review_response_ready_count']}")
    print(f"real_external_review_ready={audit['real_external_review_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()