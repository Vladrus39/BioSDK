"""Minimal BioSDK v5.22 public examples manifest example."""
from __future__ import annotations

import json

from biogpu.sdk.public_examples_v522 import build_biosdk_public_examples_gate_v522


def main() -> int:
    summary = build_biosdk_public_examples_gate_v522(".")
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "active_phase": summary["active_phase"],
                "bic_os_locked": summary["bic_os_phase_locked"],
                "public_examples_ready": summary["public_examples_ready"],
                "ready_required_public_example_count": summary["ready_required_public_example_count"],
                "required_public_example_count": summary["required_public_example_count"],
                "external_partner_evidence_ready": summary["external_partner_evidence_ready"],
                "vendor_user_evidence_ready": summary["vendor_user_evidence_ready"],
                "blocked_example_count": summary["blocked_example_count"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
