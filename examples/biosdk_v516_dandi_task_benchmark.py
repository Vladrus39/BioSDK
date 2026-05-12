"""Minimal BioSDK v5.16 DANDI/NWB task benchmark example."""
from __future__ import annotations

import json

from biogpu.sdk.nwb_task_benchmark_v516 import build_dandi_nwb_sdk_benchmark_v516


def main() -> int:
    summary = build_dandi_nwb_sdk_benchmark_v516(".", label_shuffles=25)
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "active_phase": summary["active_phase"],
                "bic_os_locked": summary["bic_os_phase_locked"],
                "sample_count": summary.get("sample_count"),
                "unit_count": summary.get("unit_count"),
                "label_counts": summary.get("label_counts"),
                "observed": summary.get("observed"),
                "label_shuffle_baseline": summary.get("label_shuffle_baseline"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
