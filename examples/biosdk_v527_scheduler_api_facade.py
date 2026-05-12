"""Minimal BioGPU v5.27 scheduler API facade example."""
from __future__ import annotations

import json

from biogpu.runtime.scheduler_api_v527 import run_scheduler_api_facade_workflow_v527


def main() -> int:
    audit = run_scheduler_api_facade_workflow_v527(".")
    print(
        json.dumps(
            {
                "overall_status": audit["overall_status"],
                "scheduler_api_facade_ready": audit["scheduler_api_facade_ready"],
                "api_route_count": audit["api_route_count"],
                "cancel_semantics_passed": audit["cancel_semantics_passed"],
                "timeout_semantics_passed": audit["timeout_semantics_passed"],
                "retry_semantics_passed": audit["retry_semantics_passed"],
                "production_api_ready": audit["production_api_ready"],
                "bic_os_phase_locked": audit["bic_os_phase_locked"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())