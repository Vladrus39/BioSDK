"""Runner for BioGPU-Core v5.34 tamper-evident incident ledger proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.incident_ledger_v534 import DEFAULT_OUT, run_tamper_evident_incident_ledger_workflow_v534, write_tamper_evident_incident_ledger_outputs_v534


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_tamper_evident_incident_ledger_workflow_v534(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_tamper_evident_incident_ledger_outputs_v534(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.34 tamper-evident incident ledger proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v534_tamper_evident_incident_ledger status={summary['overall_status']}")
    print(f"tamper_evident_incident_ledger_ready={summary['tamper_evident_incident_ledger_ready']}")
    print(f"incident_ledger_chain_valid={summary['incident_ledger_chain_valid']}")
    print(f"local_signature_validation_ready={summary['local_signature_validation_ready']}")
    print(f"retention_manifest_anchored={summary['retention_manifest_anchored']}")
    print(f"tamper_detection_passed={summary['tamper_detection_passed']}")
    print(f"incident_ledger_bundle_ready={summary['incident_ledger_bundle_ready']}")
    print(f"production_incident_ledger_ready={summary['production_incident_ledger_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()