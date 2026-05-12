from __future__ import annotations

from pathlib import Path

from biogpu.runtime.incident_workflow_v533 import run_operator_incident_retention_workflow_v533, write_operator_incident_retention_outputs_v533


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v533_operator_incident_retention_example"
    audit = run_operator_incident_retention_workflow_v533(root, out)
    write_operator_incident_retention_outputs_v533(audit, out)
    print(audit["overall_status"])
    print(f"operator_incident_retention_ready={audit['operator_incident_retention_ready']}")
    print(f"active_incident_id={audit['active_incident_id']}")
    print(f"production_incident_retention_ready={audit['production_incident_retention_ready']}")


if __name__ == "__main__":
    main()