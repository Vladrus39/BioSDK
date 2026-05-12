"""Runner for BioGPU-Core v5.35 tenant incident permissions proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.incident_permissions_v535 import DEFAULT_OUT, run_tenant_incident_permissions_workflow_v535, write_tenant_incident_permissions_outputs_v535


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_tenant_incident_permissions_workflow_v535(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_tenant_incident_permissions_outputs_v535(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.35 tenant incident permissions proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v535_tenant_incident_permissions status={summary['overall_status']}")
    print(f"tenant_incident_permissions_ready={summary['tenant_incident_permissions_ready']}")
    print(f"permission_matrix_ready={summary['permission_matrix_ready']}")
    print(f"tenant_isolation_passed={summary['tenant_isolation_passed']}")
    print(f"viewer_write_denial_passed={summary['viewer_write_denial_passed']}")
    print(f"ledger_validation_scope_passed={summary['ledger_validation_scope_passed']}")
    print(f"production_auth_ready={summary['production_auth_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()