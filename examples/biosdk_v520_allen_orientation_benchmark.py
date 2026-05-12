"""Minimal BioSDK v5.20 Allen orientation benchmark example."""
from __future__ import annotations

import json

from biogpu.sdk.allen_orientation_benchmark_v520 import build_allen_orientation_sdk_benchmark_v520


def main() -> int:
    summary = build_allen_orientation_sdk_benchmark_v520(".", top_units=32, max_windows=800, label_shuffles=25)
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "active_phase": summary["active_phase"],
                "bic_os_locked": summary["bic_os_phase_locked"],
                "sample_count": summary.get("sample_count"),
                "selected_unit_count": summary.get("selected_unit_count"),
                "feature_count": summary.get("feature_count"),
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
