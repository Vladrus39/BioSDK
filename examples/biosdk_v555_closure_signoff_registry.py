from __future__ import annotations

from pathlib import Path

from biogpu.sdk.closure_signoff_registry_v555 import run_closure_signoff_registry_workflow_v555, write_closure_signoff_registry_outputs_v555


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v555_closure_signoff_registry_example"
    audit = run_closure_signoff_registry_workflow_v555(root, out)
    write_closure_signoff_registry_outputs_v555(audit, out)
    print(audit["overall_status"])
    print(f"closure_signoff_registry_contract_ready={audit['closure_signoff_registry_contract_ready']}")
    print(f"real_external_reviewer_signoff_ready_count={audit['real_external_reviewer_signoff_ready_count']}")
    print(f"real_closure_signoff_ready_count={audit['real_closure_signoff_ready_count']}")
    print(f"production_distance={audit['production_distance_assessment']['distance']}")
    print(f"bic_os_distance={audit['bic_os_distance_assessment']['distance']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()