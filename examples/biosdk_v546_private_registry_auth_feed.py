from __future__ import annotations

from pathlib import Path

from biogpu.sdk.private_registry_auth_feed_v546 import run_private_registry_auth_feed_workflow_v546, write_private_registry_auth_feed_outputs_v546


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v546_private_registry_auth_feed_example"
    audit = run_private_registry_auth_feed_workflow_v546(root, out)
    write_private_registry_auth_feed_outputs_v546(audit, out)
    print(audit["overall_status"])
    print(f"private_registry_auth_feed_contract_ready={audit['private_registry_auth_feed_contract_ready']}")
    print(f"auth_feed_matrix_ready={audit['auth_feed_matrix_ready']}")
    print(f"expiring_feed_probe_ready={audit['expiring_feed_probe_ready']}")
    print(f"registry_log_export_contract_ready={audit['registry_log_export_contract_ready']}")
    print(f"real_private_registry_auth_ready={audit['real_private_registry_auth_ready']}")


if __name__ == "__main__":
    main()