from __future__ import annotations

from pathlib import Path

from biogpu.sdk.private_registry_handoff_v544 import run_private_registry_handoff_workflow_v544, write_private_registry_handoff_outputs_v544


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v544_private_registry_handoff_example"
    audit = run_private_registry_handoff_workflow_v544(root, out)
    write_private_registry_handoff_outputs_v544(audit, out)
    print(audit["overall_status"])
    print(f"private_registry_handoff_contract_ready={audit['private_registry_handoff_contract_ready']}")
    print(f"local_handoff_package_ready={audit['local_handoff_package_ready']}")
    print(f"live_private_registry_ready={audit['live_private_registry_ready']}")
    print(f"full_biosdk_ready={audit['full_biosdk_ready']}")


if __name__ == "__main__":
    main()