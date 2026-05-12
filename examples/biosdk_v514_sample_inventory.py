"""Minimal BioSDK v5.14 sample inventory example."""
from __future__ import annotations

import json

from biogpu.sdk.sample_acquisition_v514 import build_sample_acquisition_gate_v514


def main() -> int:
    gate = build_sample_acquisition_gate_v514(".")
    print(
        json.dumps(
            {
                "overall_status": gate["overall_status"],
                "active_phase": gate["active_phase"],
                "bic_os_locked": gate["bic_os_phase_locked"],
                "local_sources": gate["locally_available_source_families"],
                "missing_required_sample_ids": gate["missing_required_sample_ids"],
                "next_best_steps": gate["next_best_steps"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
