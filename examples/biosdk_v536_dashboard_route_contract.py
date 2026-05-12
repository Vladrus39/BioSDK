from __future__ import annotations

from pathlib import Path

from biogpu.runtime.dashboard_routes_v536 import run_dashboard_route_contract_workflow_v536, write_dashboard_route_contract_outputs_v536


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v536_dashboard_route_contract_example"
    audit = run_dashboard_route_contract_workflow_v536(root, out)
    write_dashboard_route_contract_outputs_v536(audit, out)
    print(audit["overall_status"])
    print(f"dashboard_route_contract_ready={audit['dashboard_route_contract_ready']}")
    print(f"production_dashboard_ready={audit['production_dashboard_ready']}")
    print(f"model_plus_os_path={audit['direct_answer']['are_we_configured_to_move_to_model_plus_os_after_real_proof']}")


if __name__ == "__main__":
    main()