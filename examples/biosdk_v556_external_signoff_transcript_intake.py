from __future__ import annotations

from pathlib import Path

from biogpu.sdk.external_signoff_transcript_intake_v556 import run_external_signoff_transcript_intake_workflow_v556, write_external_signoff_transcript_intake_outputs_v556


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v556_external_signoff_transcript_intake_example"
    audit = run_external_signoff_transcript_intake_workflow_v556(root, out)
    write_external_signoff_transcript_intake_outputs_v556(audit, out)
    print(audit["overall_status"])
    print(f"external_signoff_transcript_intake_contract_ready={audit['external_signoff_transcript_intake_contract_ready']}")
    print(f"real_external_signoff_accepted_count={audit['real_external_signoff_accepted_count']}")
    print(f"signed_closure_transcript_accepted_count={audit['signed_closure_transcript_accepted_count']}")
    print(f"production_distance={audit['production_distance_assessment']['distance']}")
    print(f"bic_os_distance={audit['bic_os_distance_assessment']['distance']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()