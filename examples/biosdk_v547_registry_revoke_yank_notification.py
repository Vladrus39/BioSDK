from __future__ import annotations

from pathlib import Path

from biogpu.sdk.registry_revoke_yank_notification_v547 import run_registry_revoke_yank_notification_workflow_v547, write_registry_revoke_yank_notification_outputs_v547


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v547_registry_revoke_yank_notification_example"
    audit = run_registry_revoke_yank_notification_workflow_v547(root, out)
    write_registry_revoke_yank_notification_outputs_v547(audit, out)
    print(audit["overall_status"])
    print(f"registry_revoke_yank_notification_contract_ready={audit['registry_revoke_yank_notification_contract_ready']}")
    print(f"local_yank_manifest_ready={audit['local_yank_manifest_ready']}")
    print(f"recipient_notification_ack_trail_ready={audit['recipient_notification_ack_trail_ready']}")
    print(f"incident_linkage_export_ready={audit['incident_linkage_export_ready']}")
    print(f"production_yank_ready={audit['production_yank_ready']}")


if __name__ == "__main__":
    main()