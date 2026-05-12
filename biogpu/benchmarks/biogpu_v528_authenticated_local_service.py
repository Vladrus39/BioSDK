"""Runner for BioGPU-Core v5.28 authenticated local service proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.local_service_v528 import DEFAULT_OUT, run_authenticated_local_service_workflow_v528, write_authenticated_local_service_outputs_v528


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_authenticated_local_service_workflow_v528(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_authenticated_local_service_outputs_v528(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.28 authenticated local service proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v528_authenticated_local_service status={summary['overall_status']}")
    print(f"authenticated_local_service_ready={summary['authenticated_local_service_ready']}")
    print(f"api_routes={summary['api_route_count']}")
    print(f"auth_required_for_v1={summary['auth_required_for_v1']}")
    print(f"scope_denial_passed={summary['scope_denial_passed']}")
    print(f"result_bundle_download_contract_passed={summary['result_bundle_download_contract_passed']}")
    print(f"production_api_ready={summary['production_api_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()