from __future__ import annotations

from pathlib import Path

from biogpu.sdk.external_acceptance_intake_v550 import run_external_acceptance_intake_workflow_v550, write_external_acceptance_intake_outputs_v550


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v550_external_acceptance_intake_example"
    audit = run_external_acceptance_intake_workflow_v550(root, out)
    write_external_acceptance_intake_outputs_v550(audit, out)
    print(audit["overall_status"])
    print(f"external_acceptance_intake_contract_ready={audit['external_acceptance_intake_contract_ready']}")
    print(f"schema_valid_record_count={audit['schema_valid_record_count']}")
    print(f"real_acceptance_ready_count={audit['real_acceptance_ready_count']}")
    print(f"real_external_pilot_ready={audit['real_external_pilot_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()