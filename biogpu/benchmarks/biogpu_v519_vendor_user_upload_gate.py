"""BioGPU-Core v5.19 vendor/user-upload read-only sample gate runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.vendor_upload_v519 import DEFAULT_OUT, write_vendor_upload_outputs_v519


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    paths = write_vendor_upload_outputs_v519(root=root, out_dir=out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v519_vendor_user_upload status={summary['overall_status']}")
    print(f"samples={summary['sample_count']}")
    print(f"validated_samples={summary['validated_sample_count']}")
    print(f"blocked_samples={summary['blocked_sample_count']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.19 vendor/user-upload read-only gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
