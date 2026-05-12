"""Runner for BioGPU-Core v5.42 signed artifact provenance contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.artifact_provenance_v542 import DEFAULT_OUT, run_signed_artifact_provenance_workflow_v542, write_signed_artifact_provenance_outputs_v542


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_signed_artifact_provenance_workflow_v542(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_signed_artifact_provenance_outputs_v542(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.42 signed artifact provenance contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v542_signed_artifact_provenance status={summary['overall_status']}")
    print(f"signed_artifact_provenance_contract_ready={summary['signed_artifact_provenance_contract_ready']}")
    print(f"v541_dependency_ready={summary['v541_dependency_ready']}")
    print(f"artifact_manifest_ready={summary['artifact_manifest_ready']}")
    print(f"local_signature_ready={summary['local_signature_ready']}")
    print(f"signature_validation_ready={summary['signature_validation_ready']}")
    print(f"tamper_detection_ready={summary['tamper_detection_ready']}")
    print(f"trusted_external_signature_ready={summary['trusted_external_signature_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()