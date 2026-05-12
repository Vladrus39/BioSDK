"""BioGPU-Core v5.26 durable scheduler worker proof runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.runtime.durable_scheduler_v526 import DEFAULT_OUT, run_durable_scheduler_workflow_v526, write_durable_scheduler_outputs_v526


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_durable_scheduler_workflow_v526(root=root, out_dir=out_dir)
    output_path = Path(root).resolve() / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_durable_scheduler_outputs_v526(audit, output_path)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v526_durable_scheduler_worker status={summary['overall_status']}")
    print(f"durable_scheduler_worker_proof_ready={summary['durable_scheduler_worker_proof_ready']}")
    print(f"persisted_jobs={summary['persisted_job_count']}")
    print(f"succeeded_jobs={summary['succeeded_job_count']}")
    print(f"production_scheduler_ready={summary['production_scheduler_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.26 durable scheduler worker proof")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()