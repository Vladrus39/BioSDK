"""Runner for BioGPU-Core v5.29 supervised local runtime proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.supervised_runtime_v529 import DEFAULT_OUT, run_supervised_runtime_workflow_v529, write_supervised_runtime_outputs_v529


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_supervised_runtime_workflow_v529(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_supervised_runtime_outputs_v529(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.29 supervised local runtime proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v529_supervised_runtime status={summary['overall_status']}")
    print(f"supervised_local_runtime_ready={summary['supervised_local_runtime_ready']}")
    print(f"heartbeat_index={summary['heartbeat_index']}")
    print(f"worker_tick_semantics_passed={summary['worker_tick_semantics_passed']}")
    print(f"graceful_shutdown_semantics_passed={summary['graceful_shutdown_semantics_passed']}")
    print(f"audit_export_semantics_passed={summary['audit_export_semantics_passed']}")
    print(f"production_runtime_ready={summary['production_runtime_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()