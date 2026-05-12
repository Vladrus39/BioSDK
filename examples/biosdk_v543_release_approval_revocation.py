from __future__ import annotations

from pathlib import Path

from biogpu.sdk.release_approval_v543 import run_release_approval_revocation_workflow_v543, write_release_approval_revocation_outputs_v543


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v543_release_approval_revocation_example"
    audit = run_release_approval_revocation_workflow_v543(root, out)
    write_release_approval_revocation_outputs_v543(audit, out)
    print(audit["overall_status"])
    print(f"release_approval_revocation_contract_ready={audit['release_approval_revocation_contract_ready']}")
    print(f"local_candidate_handoff_approved={audit['local_candidate_handoff_approved']}")
    print(f"production_release_approved={audit['production_release_approved']}")
    print(f"full_biosdk_ready={audit['full_biosdk_ready']}")


if __name__ == "__main__":
    main()