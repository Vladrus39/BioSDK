"""BioGPU-Core v5.25 BioSDK release-candidate evidence runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.release_candidate_evidence_v525 import DEFAULT_OUT, build_biosdk_release_candidate_evidence_v525, write_biosdk_release_candidate_evidence_outputs_v525


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_biosdk_release_candidate_evidence_v525(root)
    paths = write_biosdk_release_candidate_evidence_outputs_v525(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v525_biosdk_rc_evidence status={summary['overall_status']}")
    print(f"rc_evidence_ready={summary['biosdk_release_candidate_evidence_ready']}")
    print(f"ready_required_items={summary['ready_required_item_count']}/{summary['required_item_count']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.25 BioSDK release-candidate evidence")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()