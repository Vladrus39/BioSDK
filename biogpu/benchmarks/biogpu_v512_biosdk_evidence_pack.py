"""BioGPU-Core v5.12 BioSDK evidence pack runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.evidence_pack_v512 import DEFAULT_OUT, build_biosdk_evidence_pack_v512, write_biosdk_evidence_pack_outputs_v512


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_biosdk_evidence_pack_v512(root)
    paths = write_biosdk_evidence_pack_outputs_v512(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v512_biosdk_evidence_pack status={summary['overall_status']}")
    print(f"sdk_name={summary['sdk_name']}")
    print(f"biosdk_evidence_kernel_ready={summary['biosdk_evidence_kernel_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"locally_proven_capability_count={summary['locally_proven_capability_count']}/{summary['capability_count']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.12 BioSDK evidence pack")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
