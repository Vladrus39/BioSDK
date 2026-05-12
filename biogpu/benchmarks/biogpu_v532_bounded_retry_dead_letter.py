"""Runner for BioGPU-Core v5.32 bounded retry/dead-letter proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.retry_policy_v532 import DEFAULT_OUT, run_bounded_retry_dead_letter_workflow_v532, write_bounded_retry_dead_letter_outputs_v532


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_bounded_retry_dead_letter_workflow_v532(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_bounded_retry_dead_letter_outputs_v532(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.32 bounded retry/dead-letter proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v532_bounded_retry_dead_letter status={summary['overall_status']}")
    print(f"bounded_retry_dead_letter_ready={summary['bounded_retry_dead_letter_ready']}")
    print(f"bounded_retry_policy_ready={summary['bounded_retry_policy_ready']}")
    print(f"dead_letter_queue_ready={summary['dead_letter_queue_ready']}")
    print(f"max_attempts_enforced={summary['max_attempts_enforced']}")
    print(f"retry_backoff_metadata_ready={summary['retry_backoff_metadata_ready']}")
    print(f"production_retry_policy_ready={summary['production_retry_policy_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()