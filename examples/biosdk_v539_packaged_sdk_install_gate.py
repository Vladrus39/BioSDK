from __future__ import annotations

from pathlib import Path

from biogpu.sdk.package_install_gate_v539 import run_packaged_sdk_install_gate_workflow_v539, write_packaged_sdk_install_gate_outputs_v539


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v539_packaged_sdk_install_gate_example"
    audit = run_packaged_sdk_install_gate_workflow_v539(root, out, build_distribution=False, require_wheel_build=False)
    write_packaged_sdk_install_gate_outputs_v539(audit, out)
    print(audit["overall_status"])
    print(f"packaged_sdk_install_gate_ready={audit['packaged_sdk_install_gate_ready']}")
    print(f"local_wheel_build_ready={audit['local_wheel_build_ready']}")
    print(f"full_biosdk_ready={audit['full_biosdk_ready']}")


if __name__ == "__main__":
    main()