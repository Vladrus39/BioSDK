"""Runner for BioGPU-Core v5.30 runtime observability proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.observability_v530 import DEFAULT_OUT, run_runtime_observability_workflow_v530, write_runtime_observability_outputs_v530


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_runtime_observability_workflow_v530(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_runtime_observability_outputs_v530(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.30 runtime observability proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v530_runtime_observability status={summary['overall_status']}")
    print(f"runtime_observability_ready={summary['runtime_observability_ready']}")
    print(f"local_metrics_snapshot_ready={summary['local_metrics_snapshot_ready']}")
    print(f"status_snapshot_count={summary['status_snapshot_count']}")
    print(f"retention_policy_contract_ready={summary['retention_policy_contract_ready']}")
    print(f"pruned_audit_event_count={summary['pruned_audit_event_count']}")
    print(f"production_metrics_ready={summary['production_metrics_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()