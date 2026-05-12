"""Minimal BioSDK v5.13 public facade example."""
from __future__ import annotations

import json

from biogpu.sdk.core_v513 import run_biosdk_reference_flow_v513


def main() -> int:
    flow = run_biosdk_reference_flow_v513(".")
    summary = {
        "active_phase": flow["phase_gate"]["active_phase"],
        "bic_os_locked": flow["phase_gate"]["bic_os_phase_locked"],
        "nsi_manifest_valid": flow["nsi_manifest_valid"],
        "queue_admission_accepted": flow["queue_admission_accepted"],
        "job_status": flow["job_status"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
