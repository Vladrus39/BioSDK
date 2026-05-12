"""BioGPU-Core v5.5 Control Plane Queue Bridge runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.beta.control_plane_v55 import control_plane_summary_v55, reference_queue_demo_v55


DEFAULT_OUT = Path("outputs/v55_control_plane_queue")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _report(summary: dict[str, Any]) -> str:
    return "\n".join([
        "# BioGPU-Core v5.5 Control Plane Queue Bridge Report",
        "",
        "## Summary",
        "",
        f"- Queued demo jobs: {summary['queued_job_count']}",
        f"- Safe replay admitted: {summary['safe_replay_admitted']}",
        f"- Enterprise live-shadow admitted: {summary['live_shadow_enterprise_admitted']}",
        f"- Developer live-shadow rejected: {summary['live_shadow_developer_rejected']}",
        f"- Blocked actuation rejected: {summary['blocked_actuation_rejected']}",
        "",
        "## Boundary",
        "",
        "v5.5 admits only approved v5.4 agent responses with valid NSI task manifests. It keeps live actuation disabled and gates live-shadow by tier.",
        "",
    ])


def run(out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    demo = reference_queue_demo_v55()
    summary = control_plane_summary_v55()
    _write_json(out / "V55_CONTROL_PLANE_QUEUE_DEMO.json", demo)
    _write_json(out / "V55_CONTROL_PLANE_QUEUE_SUMMARY.json", summary)
    (out / "BIOGPU_V55_CONTROL_PLANE_QUEUE_REPORT.md").write_text(_report(summary), encoding="utf-8")
    print(f"v55_control_plane_queue queued_job_count={summary['queued_job_count']}")
    print(f"safe_replay_admitted={summary['safe_replay_admitted']}")
    print(f"blocked_actuation_rejected={summary['blocked_actuation_rejected']}")
    return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.5 Control Plane Queue Bridge runner")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(args.out_dir)


if __name__ == "__main__":
    main()
