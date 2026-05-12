"""Runner for BioGPU-Core v5.33 operator incident retention proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.incident_workflow_v533 import DEFAULT_OUT, run_operator_incident_retention_workflow_v533, write_operator_incident_retention_outputs_v533


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_operator_incident_retention_workflow_v533(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_operator_incident_retention_outputs_v533(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.33 operator incident retention proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v533_operator_incident_retention status={summary['overall_status']}")
    print(f"operator_incident_retention_ready={summary['operator_incident_retention_ready']}")
    print(f"operator_acknowledgement_ready={summary['operator_acknowledgement_ready']}")
    print(f"incident_resolution_ready={summary['incident_resolution_ready']}")
    print(f"incident_retention_manifest_ready={summary['incident_retention_manifest_ready']}")
    print(f"incident_audit_bundle_ready={summary['incident_audit_bundle_ready']}")
    print(f"production_incident_retention_ready={summary['production_incident_retention_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()