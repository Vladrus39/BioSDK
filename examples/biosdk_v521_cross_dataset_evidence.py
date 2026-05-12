"""Minimal BioSDK v5.21 cross-dataset evidence example."""
from __future__ import annotations

import json

from biogpu.sdk.cross_dataset_evidence_v521 import build_cross_dataset_evidence_pack_v521


def main() -> int:
    summary = build_cross_dataset_evidence_pack_v521(".")
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "active_phase": summary["active_phase"],
                "bic_os_locked": summary["bic_os_phase_locked"],
                "public_cross_dataset_evidence_ready": summary["public_cross_dataset_evidence_ready"],
                "public_benchmark_source_count": summary["public_benchmark_source_count"],
                "public_source_target": summary["public_source_target"],
                "external_partner_evidence_ready": summary["external_partner_evidence_ready"],
                "vendor_user_evidence_ready": summary["vendor_user_evidence_ready"],
                "missing_required_sample_ids": summary["missing_required_sample_ids"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
