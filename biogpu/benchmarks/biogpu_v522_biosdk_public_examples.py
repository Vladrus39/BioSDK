"""BioGPU-Core v5.22 BioSDK public examples runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.public_examples_v522 import DEFAULT_OUT, build_biosdk_public_examples_gate_v522, write_biosdk_public_examples_outputs_v522


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_biosdk_public_examples_gate_v522(root)
    paths = write_biosdk_public_examples_outputs_v522(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v522_biosdk_public_examples status={summary['overall_status']}")
    print(f"public_examples_ready={summary['public_examples_ready']}")
    print(f"ready_required_public_examples={summary['ready_required_public_example_count']}/{summary['required_public_example_count']}")
    print(f"external_partner_evidence_ready={summary['external_partner_evidence_ready']}")
    print(f"vendor_user_evidence_ready={summary['vendor_user_evidence_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.22 BioSDK public examples")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
