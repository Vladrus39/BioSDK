"""BioGPU-Core v5.10 project alignment and claim audit runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.claims.project_alignment_v510 import DEFAULT_OUT, build_project_alignment_audit_v510, write_project_alignment_outputs_v510


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_project_alignment_audit_v510(root)
    paths = write_project_alignment_outputs_v510(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v510_project_alignment_claim_audit status={summary['overall_status']}")
    print(f"did_we_drift_from_project_meaning={summary['direct_answer']['did_we_drift_from_project_meaning']}")
    print(f"is_global_uniqueness_proven={summary['direct_answer']['is_the_code_globally_unique_proven']}")
    print(f"claim_status_counts={summary['status_counts']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.10 project alignment and claim audit")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
