from __future__ import annotations

from pathlib import Path

from biogpu.sdk.partner_dataroom_review_packet_v551 import run_partner_dataroom_review_packet_workflow_v551, write_partner_dataroom_review_packet_outputs_v551


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v551_partner_dataroom_review_packet_example"
    audit = run_partner_dataroom_review_packet_workflow_v551(root, out)
    write_partner_dataroom_review_packet_outputs_v551(audit, out)
    print(audit["overall_status"])
    print(f"partner_dataroom_review_packet_contract_ready={audit['partner_dataroom_review_packet_contract_ready']}")
    print(f"local_manifest_item_ready_count={audit['local_manifest_item_ready_count']}")
    print(f"real_dataroom_item_ready_count={audit['real_dataroom_item_ready_count']}")
    print(f"real_external_review_ready={audit['real_external_review_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()