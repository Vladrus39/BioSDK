"""Runner for BioGPU-Core v5.43 release approval and revocation contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.release_approval_v543 import DEFAULT_OUT, run_release_approval_revocation_workflow_v543, write_release_approval_revocation_outputs_v543


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_release_approval_revocation_workflow_v543(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_release_approval_revocation_outputs_v543(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.43 release approval and revocation contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v543_release_approval_revocation status={summary['overall_status']}")
    print(f"release_approval_revocation_contract_ready={summary['release_approval_revocation_contract_ready']}")
    print(f"v542_dependency_ready={summary['v542_dependency_ready']}")
    print(f"release_approval_matrix_ready={summary['release_approval_matrix_ready']}")
    print(f"release_revocation_drill_ready={summary['release_revocation_drill_ready']}")
    print(f"local_candidate_handoff_approved={summary['local_candidate_handoff_approved']}")
    print(f"production_release_approved={summary['production_release_approved']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()