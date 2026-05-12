from __future__ import annotations

from pathlib import Path

from biogpu.runtime.incident_ledger_v534 import run_tamper_evident_incident_ledger_workflow_v534, write_tamper_evident_incident_ledger_outputs_v534


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v534_tamper_evident_incident_ledger_example"
    audit = run_tamper_evident_incident_ledger_workflow_v534(root, out)
    write_tamper_evident_incident_ledger_outputs_v534(audit, out)
    print(audit["overall_status"])
    print(f"tamper_evident_incident_ledger_ready={audit['tamper_evident_incident_ledger_ready']}")
    print(f"entry_count={audit['entry_count']}")
    print(f"production_incident_ledger_ready={audit['production_incident_ledger_ready']}")


if __name__ == "__main__":
    main()