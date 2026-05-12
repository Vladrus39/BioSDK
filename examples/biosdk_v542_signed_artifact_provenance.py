from __future__ import annotations

from pathlib import Path

from biogpu.sdk.artifact_provenance_v542 import run_signed_artifact_provenance_workflow_v542, write_signed_artifact_provenance_outputs_v542


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v542_signed_artifact_provenance_example"
    audit = run_signed_artifact_provenance_workflow_v542(root, out)
    write_signed_artifact_provenance_outputs_v542(audit, out)
    print(audit["overall_status"])
    print(f"signed_artifact_provenance_contract_ready={audit['signed_artifact_provenance_contract_ready']}")
    print(f"local_signature_ready={audit['local_signature_ready']}")
    print(f"trusted_external_signature_ready={audit['trusted_external_signature_ready']}")
    print(f"full_biosdk_ready={audit['full_biosdk_ready']}")


if __name__ == "__main__":
    main()