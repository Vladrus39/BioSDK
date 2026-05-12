from __future__ import annotations

from pathlib import Path

from biogpu.sdk.clean_room_install_report_v541 import run_clean_room_install_report_workflow_v541, write_clean_room_install_report_outputs_v541


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v541_clean_room_install_report_example"
    audit = run_clean_room_install_report_workflow_v541(root, out, run_local_install_probe=False, require_local_install_probe=False)
    write_clean_room_install_report_outputs_v541(audit, out)
    print(audit["overall_status"])
    print(f"clean_room_install_report_contract_ready={audit['clean_room_install_report_contract_ready']}")
    print(f"external_clean_room_report_ready={audit['external_clean_room_report_ready']}")
    print(f"full_biosdk_ready={audit['full_biosdk_ready']}")


if __name__ == "__main__":
    main()