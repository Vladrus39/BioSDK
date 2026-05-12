from __future__ import annotations

from pathlib import Path

from biogpu.runtime.incident_permissions_v535 import run_tenant_incident_permissions_workflow_v535, write_tenant_incident_permissions_outputs_v535


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v535_tenant_incident_permissions_example"
    audit = run_tenant_incident_permissions_workflow_v535(root, out)
    write_tenant_incident_permissions_outputs_v535(audit, out)
    print(audit["overall_status"])
    print(f"tenant_incident_permissions_ready={audit['tenant_incident_permissions_ready']}")
    print(f"production_auth_ready={audit['production_auth_ready']}")
    print(f"local_only_correct_now={audit['direct_answer']['is_local_only_the_right_mode_now']}")


if __name__ == "__main__":
    main()