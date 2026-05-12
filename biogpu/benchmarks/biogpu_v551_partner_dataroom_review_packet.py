"""Runner for BioGPU-Core v5.51 partner data-room review packet proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.partner_dataroom_review_packet_v551 import DEFAULT_OUT, run_partner_dataroom_review_packet_workflow_v551, write_partner_dataroom_review_packet_outputs_v551


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_partner_dataroom_review_packet_workflow_v551(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_partner_dataroom_review_packet_outputs_v551(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.51 partner data-room review packet proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v551_partner_dataroom_review_packet status={summary['overall_status']}")
    print(f"partner_dataroom_review_packet_contract_ready={summary['partner_dataroom_review_packet_contract_ready']}")
    print(f"v550_dependency_ready={summary['v550_dependency_ready']}")
    print(f"partner_dataroom_manifest_ready={summary['partner_dataroom_manifest_ready']}")
    print(f"external_review_packet_ready={summary['external_review_packet_ready']}")
    print(f"external_review_gate_ready={summary['external_review_gate_ready']}")
    print(f"real_dataroom_item_ready_count={summary['real_dataroom_item_ready_count']}")
    print(f"real_external_review_ready={summary['real_external_review_ready']}")
    print(f"real_external_pilot_ready={summary['real_external_pilot_ready']}")
    print(f"production_ready={summary['production_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()