"""Runner for BioGPU-Core v5.56 external signoff transcript intake proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.external_signoff_transcript_intake_v556 import DEFAULT_OUT, run_external_signoff_transcript_intake_workflow_v556, write_external_signoff_transcript_intake_outputs_v556


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_external_signoff_transcript_intake_workflow_v556(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_external_signoff_transcript_intake_outputs_v556(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.56 external signoff transcript intake proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v556_external_signoff_transcript_intake status={summary['overall_status']}")
    print(f"external_signoff_transcript_intake_contract_ready={summary['external_signoff_transcript_intake_contract_ready']}")
    print(f"v555_dependency_ready={summary['v555_dependency_ready']}")
    print(f"external_signoff_intake_matrix_ready={summary['external_signoff_intake_matrix_ready']}")
    print(f"signed_closure_transcript_packet_ready={summary['signed_closure_transcript_packet_ready']}")
    print(f"transcript_acceptance_gate_ready={summary['transcript_acceptance_gate_ready']}")
    print(f"real_external_signoff_accepted_count={summary['real_external_signoff_accepted_count']}")
    print(f"signed_closure_transcript_accepted_count={summary['signed_closure_transcript_accepted_count']}")
    print(f"review_finding_closed_count={summary['review_finding_closed_count']}")
    print(f"production_distance={summary['production_distance_assessment']['distance']}")
    print(f"bic_os_distance={summary['bic_os_distance_assessment']['distance']}")
    print(f"production_ready={summary['production_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()