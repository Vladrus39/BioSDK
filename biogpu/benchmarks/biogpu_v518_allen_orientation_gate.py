"""BioGPU-Core v5.18 Allen visual-coding orientation gate runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.allen_orientation_v518 import DEFAULT_OUT, write_allen_orientation_outputs_v518


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    paths = write_allen_orientation_outputs_v518(root=root, out_dir=out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v518_allen_orientation status={summary['overall_status']}")
    print(f"nwb_samples={summary['nwb_sample_count']}")
    print(f"manifest_assets={summary['manifest_asset_count']}")
    print(f"validated_samples={summary['validated_sample_count']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.18 Allen visual-coding orientation gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
