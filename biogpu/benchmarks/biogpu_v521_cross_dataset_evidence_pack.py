"""BioGPU-Core v5.21 cross-dataset BioSDK evidence pack runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.cross_dataset_evidence_v521 import DEFAULT_OUT, build_cross_dataset_evidence_pack_v521, write_cross_dataset_evidence_outputs_v521


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_cross_dataset_evidence_pack_v521(root)
    paths = write_cross_dataset_evidence_outputs_v521(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v521_cross_dataset_evidence status={summary['overall_status']}")
    print(f"public_cross_dataset_evidence_ready={summary['public_cross_dataset_evidence_ready']}")
    print(f"public_benchmark_sources={summary['public_benchmark_source_count']}/{summary['public_source_target']}")
    print(f"external_partner_evidence_ready={summary['external_partner_evidence_ready']}")
    print(f"vendor_user_evidence_ready={summary['vendor_user_evidence_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.21 cross-dataset BioSDK evidence pack")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
