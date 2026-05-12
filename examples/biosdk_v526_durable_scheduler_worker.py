"""Minimal BioGPU v5.26 durable scheduler worker example."""
from __future__ import annotations

import json

from biogpu.runtime.durable_scheduler_v526 import run_durable_scheduler_workflow_v526


def main() -> int:
    audit = run_durable_scheduler_workflow_v526(".")
    print(
        json.dumps(
            {
                "overall_status": audit["overall_status"],
                "proof_ready": audit["durable_scheduler_worker_proof_ready"],
                "persisted_jobs": audit["persisted_job_count"],
                "succeeded_jobs": audit["succeeded_job_count"],
                "production_scheduler_ready": audit["production_scheduler_ready"],
                "bic_os_phase_locked": audit["bic_os_phase_locked"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())