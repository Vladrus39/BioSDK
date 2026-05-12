"""BioGPU-Core v5.15 DANDI/NWB task validation runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.nwb_task_validation_v515 import DEFAULT_OUT, build_dandi_nwb_task_validation_gate_v515, write_dandi_nwb_task_outputs_v515


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    paths = write_dandi_nwb_task_outputs_v515(root, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v515_dandi_nwb_task_validation status={summary['overall_status']}")
    print(f"nwb_samples={summary['validated_sample_count']}/{summary['nwb_sample_count']}")
    print(f"total_units={summary['total_unit_count']}")
    print(f"total_spike_times={summary['total_spike_times_count']}")
    print(f"total_windows={summary['total_exported_window_count']}")
    return {"summary": summary, "gate": build_dandi_nwb_task_validation_gate_v515(root), "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.15 DANDI/NWB task validation")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
