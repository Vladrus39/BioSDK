"""Runner for BioGPU-Core v5.31 recovery alerting proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.recovery_v531 import DEFAULT_OUT, run_recovery_alerting_workflow_v531, write_recovery_alerting_outputs_v531


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_recovery_alerting_workflow_v531(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_recovery_alerting_outputs_v531(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.31 recovery alerting proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v531_recovery_alerting status={summary['overall_status']}")
    print(f"recovery_alerting_ready={summary['recovery_alerting_ready']}")
    print(f"stale_heartbeat_alert_passed={summary['stale_heartbeat_alert_passed']}")
    print(f"failure_classification_passed={summary['failure_classification_passed']}")
    print(f"worker_recovery_passed={summary['worker_recovery_passed']}")
    print(f"recovery_audit_bundle_ready={summary['recovery_audit_bundle_ready']}")
    print(f"production_recovery_ready={summary['production_recovery_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()