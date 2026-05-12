"""Runner for BioGPU-Core v5.41 clean-room install report contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.clean_room_install_report_v541 import DEFAULT_OUT, run_clean_room_install_report_workflow_v541, write_clean_room_install_report_outputs_v541


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, run_local_install_probe: bool = False, require_local_install_probe: bool = False) -> dict[str, Any]:
    audit = run_clean_room_install_report_workflow_v541(root, out_dir, run_local_install_probe=run_local_install_probe, require_local_install_probe=require_local_install_probe)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_clean_room_install_report_outputs_v541(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.41 clean-room install report contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    parser.add_argument("--run-local-install-probe", action="store_true", help="Build/install wheel into an isolated local target and record a report probe")
    parser.add_argument("--require-local-install-probe", action="store_true", help="Require the local install probe for proof readiness")
    args = parser.parse_args()
    result = run(args.root, args.out_dir, run_local_install_probe=args.run_local_install_probe, require_local_install_probe=args.require_local_install_probe)
    summary = result["summary"]
    print(f"v541_clean_room_install_report status={summary['overall_status']}")
    print(f"clean_room_install_report_contract_ready={summary['clean_room_install_report_contract_ready']}")
    print(f"v540_dependency_ready={summary['v540_dependency_ready']}")
    print(f"environment_contract_ready={summary['environment_contract_ready']}")
    print(f"report_completeness_ready={summary['report_completeness_ready']}")
    print(f"local_clean_room_install_probe_ready={summary['local_clean_room_install_probe_ready']}")
    print(f"external_clean_room_report_ready={summary['external_clean_room_report_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()