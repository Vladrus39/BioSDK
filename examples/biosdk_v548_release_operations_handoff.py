from __future__ import annotations

from pathlib import Path

from biogpu.sdk.release_operations_handoff_v548 import run_release_operations_handoff_workflow_v548, write_release_operations_handoff_outputs_v548


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v548_release_operations_handoff_example"
    audit = run_release_operations_handoff_workflow_v548(root, out)
    write_release_operations_handoff_outputs_v548(audit, out)
    print(audit["overall_status"])
    print(f"release_operations_handoff_contract_ready={audit['release_operations_handoff_contract_ready']}")
    print(f"release_operations_runbook_ready={audit['release_operations_runbook_ready']}")
    print(f"operator_handoff_matrix_ready={audit['operator_handoff_matrix_ready']}")
    print(f"production_release_ready={audit['production_release_ready']}")
    print(f"many_layers_remaining={audit['direct_answer']['do_we_still_need_many_layers_before_production_and_os']}")


if __name__ == "__main__":
    main()