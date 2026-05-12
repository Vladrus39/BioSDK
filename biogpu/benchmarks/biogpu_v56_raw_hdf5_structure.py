"""BioGPU-Core v5.6 raw HDF5 structure/event inspection runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.data_ingest.zenodo_raw_hdf5_v56 import inspect_raw_hdf5_tree_v56, write_raw_hdf5_outputs_v56


DEFAULT_ROOT = Path("data/external/raw_hdf5")
DEFAULT_OUT = Path("outputs/v56_raw_hdf5_structure")


def run(
    root: str | Path = DEFAULT_ROOT,
    out_dir: str | Path = DEFAULT_OUT,
    max_files: int | None = None,
) -> dict[str, Any]:
    report = inspect_raw_hdf5_tree_v56(root=root, max_files=max_files)
    paths = write_raw_hdf5_outputs_v56(report, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v56_raw_hdf5_structure status={summary['overall_status']}")
    print(f"hdf5_files={summary['file_count']}")
    print(f"files_with_events={summary['files_with_events']}")
    print(f"event_candidate_count={summary['event_candidate_count']}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.6 raw HDF5 structure/event inspection")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--max-files", type=int, default=None)
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir, max_files=args.max_files)


if __name__ == "__main__":
    main()
