"""BioGPU-Core v5.9 raw-native stability audit runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.analysis.raw_native_stability_v59 import (
    DEFAULT_V58_MATRIX,
    DEFAULT_V58_METADATA,
    build_raw_native_stability_audit_v59,
    load_raw_native_dataset_v59,
    write_raw_native_stability_outputs_v59,
)
from biogpu.benchmarks.biogpu_v58_raw_native_benchmark import run as run_v58_raw_native_benchmark


DEFAULT_OUT = Path("outputs/v59_raw_native_stability_audit")


def _ensure_v58_outputs(matrix_npz: str | Path, metadata_csv: str | Path) -> None:
    matrix_path = Path(matrix_npz)
    metadata_path = Path(metadata_csv)
    if matrix_path.exists() and metadata_path.exists():
        return
    run_v58_raw_native_benchmark()


def run(
    matrix_npz: str | Path = DEFAULT_V58_MATRIX,
    metadata_csv: str | Path = DEFAULT_V58_METADATA,
    out_dir: str | Path = DEFAULT_OUT,
    min_groups_per_target: int = 2,
    label_shuffles: int = 200,
    seed: int = 59,
    ensure_v58: bool = True,
) -> dict[str, Any]:
    if ensure_v58:
        _ensure_v58_outputs(matrix_npz, metadata_csv)
    dataset = load_raw_native_dataset_v59(matrix_npz=matrix_npz, metadata_csv=metadata_csv)
    audit = build_raw_native_stability_audit_v59(
        dataset,
        min_groups_per_target=min_groups_per_target,
        label_shuffles=label_shuffles,
        seed=seed,
    )
    paths = write_raw_native_stability_outputs_v59(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v59_raw_native_stability_audit status={summary['overall_status']}")
    print(f"feature_rows={summary['feature_row_count']}")
    print(f"recording_groups={summary['recording_group_count']}")
    print(f"split_half_cosine_median={summary.get('split_half_cosine_median')}")
    print(f"target_readout_signal_status={summary.get('target_readout_signal_status')}")
    print(f"target_fingerprint_signal_status={summary.get('target_fingerprint_signal_status')}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.9 raw-native stability audit")
    parser.add_argument("--matrix-npz", default=str(DEFAULT_V58_MATRIX))
    parser.add_argument("--metadata-csv", default=str(DEFAULT_V58_METADATA))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--min-groups-per-target", type=int, default=2)
    parser.add_argument("--label-shuffles", type=int, default=200)
    parser.add_argument("--seed", type=int, default=59)
    parser.add_argument("--no-ensure-v58", action="store_true")
    args = parser.parse_args()
    run(
        matrix_npz=args.matrix_npz,
        metadata_csv=args.metadata_csv,
        out_dir=args.out_dir,
        min_groups_per_target=args.min_groups_per_target,
        label_shuffles=args.label_shuffles,
        seed=args.seed,
        ensure_v58=not args.no_ensure_v58,
    )


if __name__ == "__main__":
    main()
