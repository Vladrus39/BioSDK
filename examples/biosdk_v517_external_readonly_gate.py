"""Minimal BioSDK v5.17 external read-only API gate example."""
from __future__ import annotations

import json

from biogpu.sdk.external_readonly_v517 import build_external_readonly_api_gate_v517


def main() -> int:
    gate = build_external_readonly_api_gate_v517(".")
    print(
        json.dumps(
            {
                "overall_status": gate["overall_status"],
                "active_phase": gate["active_phase"],
                "bic_os_locked": gate["bic_os_phase_locked"],
                "mock_contracts": f"{gate['mock_contract_passed_count']}/{gate['platform_count']}",
                "real_external_ready": gate["real_external_ready"],
                "required_real_external_next_steps": gate["required_real_external_next_steps"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
