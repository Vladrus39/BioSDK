"""Minimal BioSDK v5.18 Allen orientation gate example."""
from __future__ import annotations

import json

from biogpu.sdk.allen_orientation_v518 import build_allen_orientation_gate_v518


def main() -> int:
    gate = build_allen_orientation_gate_v518(".")
    print(
        json.dumps(
            {
                "overall_status": gate["overall_status"],
                "active_phase": gate["active_phase"],
                "bic_os_locked": gate["bic_os_phase_locked"],
                "nwb_sample_count": gate["nwb_sample_count"],
                "manifest_asset_count": gate["manifest_asset_count"],
                "required_next_steps": gate["required_next_steps"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
