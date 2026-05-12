"""BioGPU-Core v5.8 raw-native HDF5 benchmark runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.data_ingest.raw_native_benchmark_v58 import (
    DEFAULT_RAW_EVENT_CANDIDATES,
    DEFAULT_RAW_ROOT,
    build_raw_native_feature_matrix_v58,
    group_heldout_condition_readout_v58,
    write_raw_native_outputs_v58,
)
from biogpu.data_ingest.zenodo_raw_hdf5_v56 import inspect_raw_hdf5_tree_v56, write_raw_hdf5_outputs_v56


DEFAULT_V56_OUT = Path("outputs/v56_raw_hdf5_structure")
DEFAULT_OUT = Path("outputs/v58_raw_native_benchmark")


def _ensure_v56_event_csv(raw_root: str | Path, v56_out_dir: str | Path, raw_event_csv: str | Path) -> None:
    raw_event_path = Path(raw_event_csv)
    if raw_event_path.exists():
        return
    report = inspect_raw_hdf5_tree_v56(raw_root)
    write_raw_hdf5_outputs_v56(report, v56_out_dir)


def run(
    raw_root: str | Path = DEFAULT_RAW_ROOT,
    raw_event_csv: str | Path = DEFAULT_RAW_EVENT_CANDIDATES,
    out_dir: str | Path = DEFAULT_OUT,
    v56_out_dir: str | Path = DEFAULT_V56_OUT,
    max_events_per_recording: int = 16,
    window_pre_ms: float = 20.0,
    window_post_ms: float = 80.0,
    label_shuffles: int = 25,
    ensure_v56: bool = True,
) -> dict[str, Any]:
    if ensure_v56:
        _ensure_v56_event_csv(raw_root, v56_out_dir, raw_event_csv)
    matrix = build_raw_native_feature_matrix_v58(
        raw_root=raw_root,
        raw_event_csv=raw_event_csv,
        max_events_per_recording=max_events_per_recording,
        window_pre_ms=window_pre_ms,
        window_post_ms=window_post_ms,
    )
    readout = group_heldout_condition_readout_v58(matrix, label_shuffles=label_shuffles)
    paths = write_raw_native_outputs_v58(matrix, readout, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v58_raw_native_benchmark status={summary['overall_status']}")
    print(f"raw_event_sources={summary['raw_event_source_count']}")
    print(f"feature_rows={summary['feature_row_count']}")
    print(f"feature_count={summary['feature_count']}")
    print(f"condition_readout_status={summary.get('condition_readout_status')}")
    return {"summary": summary, "readout": readout, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.8 raw-native HDF5 benchmark")
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--raw-event-csv", default=str(DEFAULT_RAW_EVENT_CANDIDATES))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--v56-out-dir", default=str(DEFAULT_V56_OUT))
    parser.add_argument("--max-events-per-recording", type=int, default=16)
    parser.add_argument("--window-pre-ms", type=float, default=20.0)
    parser.add_argument("--window-post-ms", type=float, default=80.0)
    parser.add_argument("--label-shuffles", type=int, default=25)
    parser.add_argument("--no-ensure-v56", action="store_true")
    args = parser.parse_args()
    run(
        raw_root=args.raw_root,
        raw_event_csv=args.raw_event_csv,
        out_dir=args.out_dir,
        v56_out_dir=args.v56_out_dir,
        max_events_per_recording=args.max_events_per_recording,
        window_pre_ms=args.window_pre_ms,
        window_post_ms=args.window_post_ms,
        label_shuffles=args.label_shuffles,
        ensure_v56=not args.no_ensure_v56,
    )


if __name__ == "__main__":
    main()
