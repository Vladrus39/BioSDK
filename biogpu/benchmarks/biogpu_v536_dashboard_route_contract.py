"""Runner for BioGPU-Core v5.36 dashboard route-contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.dashboard_routes_v536 import DEFAULT_OUT, run_dashboard_route_contract_workflow_v536, write_dashboard_route_contract_outputs_v536


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_dashboard_route_contract_workflow_v536(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_dashboard_route_contract_outputs_v536(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.36 dashboard route-contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v536_dashboard_route_contract status={summary['overall_status']}")
    print(f"dashboard_route_contract_ready={summary['dashboard_route_contract_ready']}")
    print(f"route_count={summary['route_count']}")
    print(f"dashboard_access_matrix_ready={summary['dashboard_access_matrix_ready']}")
    print(f"viewer_write_denial_passed={summary['viewer_write_denial_passed']}")
    print(f"production_dashboard_ready={summary['production_dashboard_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()