"""Minimal BioSDK v5.19 vendor/user-upload gate example."""
from __future__ import annotations

import json

from biogpu.sdk.vendor_upload_v519 import build_vendor_upload_gate_v519


def main() -> int:
    gate = build_vendor_upload_gate_v519(".")
    print(
        json.dumps(
            {
                "overall_status": gate["overall_status"],
                "active_phase": gate["active_phase"],
                "bic_os_locked": gate["bic_os_phase_locked"],
                "sample_count": gate["sample_count"],
                "validated_sample_count": gate["validated_sample_count"],
                "required_next_steps": gate["required_next_steps"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
