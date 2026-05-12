"""Runner for BioGPU-Core v5.39 packaged SDK install gate proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.package_install_gate_v539 import DEFAULT_OUT, run_packaged_sdk_install_gate_workflow_v539, write_packaged_sdk_install_gate_outputs_v539


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT, build_distribution: bool = False, require_wheel_build: bool = False) -> dict[str, Any]:
    audit = run_packaged_sdk_install_gate_workflow_v539(root, out_dir, build_distribution=build_distribution, require_wheel_build=require_wheel_build)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_packaged_sdk_install_gate_outputs_v539(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.39 packaged SDK install gate proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    parser.add_argument("--build-distribution", action="store_true", help="Build and install a local wheel with no dependency download")
    parser.add_argument("--require-wheel-build", action="store_true", help="Require the wheel build/install smoke for proof readiness")
    args = parser.parse_args()
    result = run(args.root, args.out_dir, build_distribution=args.build_distribution, require_wheel_build=args.require_wheel_build)
    summary = result["summary"]
    print(f"v539_packaged_sdk_install_gate status={summary['overall_status']}")
    print(f"packaged_sdk_install_gate_ready={summary['packaged_sdk_install_gate_ready']}")
    print(f"package_metadata_contract_ready={summary['package_metadata_contract_ready']}")
    print(f"entrypoint_contract_ready={summary['entrypoint_contract_ready']}")
    print(f"local_wheel_build_ready={summary['local_wheel_build_ready']}")
    print(f"local_install_smoke_ready={summary['local_install_smoke_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()