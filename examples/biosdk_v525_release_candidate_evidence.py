"""Minimal BioSDK v5.25 release-candidate evidence example."""
from __future__ import annotations

import json

from biogpu.sdk.release_candidate_evidence_v525 import build_biosdk_release_candidate_evidence_v525


def main() -> int:
    audit = build_biosdk_release_candidate_evidence_v525(".")
    print(
        json.dumps(
            {
                "overall_status": audit["overall_status"],
                "release_candidate_label": audit["release_candidate_label"],
                "rc_evidence_ready": audit["biosdk_release_candidate_evidence_ready"],
                "ready_required_items": f"{audit['ready_required_item_count']}/{audit['required_item_count']}",
                "full_biosdk_ready": audit["full_biosdk_ready"],
                "bic_os_phase_locked": audit["bic_os_phase_locked"],
                "next_best_build_step": audit["direct_answer"]["next_best_build_step"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())