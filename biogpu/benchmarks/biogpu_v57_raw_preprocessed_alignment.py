"""BioGPU-Core v5.7 raw-vs-preprocessed alignment audit runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.data_ingest.raw_preprocessed_alignment_v57 import (
    DEFAULT_PULSE_METADATA,
    DEFAULT_RAW_EVENT_CANDIDATES,
    build_raw_preprocessed_alignment_report_v57,
    write_raw_preprocessed_alignment_outputs_v57,
)
from biogpu.data_ingest.zenodo_raw_hdf5_v56 import inspect_raw_hdf5_tree_v56, write_raw_hdf5_outputs_v56


DEFAULT_RAW_ROOT = Path("data/external/raw_hdf5")
DEFAULT_V56_OUT = Path("outputs/v56_raw_hdf5_structure")
DEFAULT_OUT = Path("outputs/v57_raw_preprocessed_alignment")


def _ensure_v56_event_csv(raw_root: str | Path, v56_out_dir: str | Path, raw_event_csv: str | Path) -> None:
    raw_event_path = Path(raw_event_csv)
    if raw_event_path.exists():
        return
    report = inspect_raw_hdf5_tree_v56(raw_root)
    write_raw_hdf5_outputs_v56(report, v56_out_dir)


def run(
    raw_event_csv: str | Path = DEFAULT_RAW_EVENT_CANDIDATES,
    pulse_metadata_csv: str | Path = DEFAULT_PULSE_METADATA,
    out_dir: str | Path = DEFAULT_OUT,
    raw_root: str | Path = DEFAULT_RAW_ROOT,
    v56_out_dir: str | Path = DEFAULT_V56_OUT,
    interval_tolerance_s: float = 0.02,
    ensure_v56: bool = True,
) -> dict[str, Any]:
    if ensure_v56:
        _ensure_v56_event_csv(raw_root, v56_out_dir, raw_event_csv)
    report = build_raw_preprocessed_alignment_report_v57(
        raw_event_csv=raw_event_csv,
        pulse_metadata_csv=pulse_metadata_csv,
        interval_tolerance_s=interval_tolerance_s,
    )
    paths = write_raw_preprocessed_alignment_outputs_v57(report, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v57_raw_preprocessed_alignment status={summary['overall_status']}")
    print(f"raw_event_recordings={summary['raw_event_recording_count']}")
    print(f"preprocessed_pulse_recordings={summary['preprocessed_pulse_recording_count']}")
    print(f"exact_recording_matches={summary['exact_recording_match_count']}")
    print(f"temporal_signature_matches={summary['temporal_signature_match_count']}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.7 raw-vs-preprocessed alignment audit")
    parser.add_argument("--raw-event-csv", default=str(DEFAULT_RAW_EVENT_CANDIDATES))
    parser.add_argument("--pulse-metadata-csv", default=str(DEFAULT_PULSE_METADATA))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--v56-out-dir", default=str(DEFAULT_V56_OUT))
    parser.add_argument("--interval-tolerance-s", type=float, default=0.02)
    parser.add_argument("--no-ensure-v56", action="store_true")
    args = parser.parse_args()
    run(
        raw_event_csv=args.raw_event_csv,
        pulse_metadata_csv=args.pulse_metadata_csv,
        out_dir=args.out_dir,
        raw_root=args.raw_root,
        v56_out_dir=args.v56_out_dir,
        interval_tolerance_s=args.interval_tolerance_s,
        ensure_v56=not args.no_ensure_v56,
    )


if __name__ == "__main__":
    main()
