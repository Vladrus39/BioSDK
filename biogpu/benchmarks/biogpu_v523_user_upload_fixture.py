"""BioGPU-Core v5.23 safe user-upload fixture runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.user_upload_fixture_v523 import DEFAULT_OUT, run_user_upload_fixture_workflow_v523, write_user_upload_fixture_outputs_v523


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, overwrite: bool = True) -> dict[str, Any]:
    audit = run_user_upload_fixture_workflow_v523(root=root, overwrite=overwrite)
    paths = write_user_upload_fixture_outputs_v523(audit, out_dir=out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v523_user_upload_fixture status={summary['overall_status']}")
    print(f"fixture_validation_status={summary['fixture_validation_status']}")
    print(f"user_upload_validated={summary['user_upload_validated']}")
    print(f"vendor_export_validated={summary['vendor_export_validated']}")
    print(f"external_partner_evidence_ready={summary['external_partner_evidence_ready']}")
    print(f"full_sample_proof_ready={summary['full_sample_proof_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.23 safe user-upload fixture")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--no-overwrite", action="store_true")
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir, overwrite=not args.no_overwrite)


if __name__ == "__main__":
    main()
