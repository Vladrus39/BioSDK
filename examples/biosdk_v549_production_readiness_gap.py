from __future__ import annotations

from pathlib import Path

from biogpu.sdk.production_readiness_gap_v549 import run_production_readiness_gap_workflow_v549, write_production_readiness_gap_outputs_v549


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v549_production_readiness_gap_example"
    audit = run_production_readiness_gap_workflow_v549(root, out)
    write_production_readiness_gap_outputs_v549(audit, out)
    print(audit["overall_status"])
    print(f"production_readiness_gap_contract_ready={audit['production_readiness_gap_contract_ready']}")
    print(f"open_gap_count={audit['open_gap_count']}")
    print(f"production_ready_domain_count={audit['production_ready_domain_count']}")
    print(f"real_external_pilot_ready={audit['real_external_pilot_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()