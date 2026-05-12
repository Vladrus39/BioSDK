from __future__ import annotations

from pathlib import Path

from biogpu.sdk.recipient_onboarding_audit_v545 import run_recipient_onboarding_audit_workflow_v545, write_recipient_onboarding_audit_outputs_v545


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v545_recipient_onboarding_audit_example"
    audit = run_recipient_onboarding_audit_workflow_v545(root, out)
    write_recipient_onboarding_audit_outputs_v545(audit, out)
    print(audit["overall_status"])
    print(f"recipient_onboarding_audit_contract_ready={audit['recipient_onboarding_audit_contract_ready']}")
    print(f"recipient_access_log_ready={audit['recipient_access_log_ready']}")
    print(f"access_expiry_probe_ready={audit['access_expiry_probe_ready']}")
    print(f"real_recipient_onboarding_ready={audit['real_recipient_onboarding_ready']}")
    print(f"live_private_registry_ready={audit['live_private_registry_ready']}")


if __name__ == "__main__":
    main()