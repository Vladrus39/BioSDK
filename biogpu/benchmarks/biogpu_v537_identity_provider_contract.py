"""Runner for BioGPU-Core v5.37 identity-provider contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.identity_provider_contract_v537 import DEFAULT_OUT, run_identity_provider_contract_workflow_v537, write_identity_provider_contract_outputs_v537


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_identity_provider_contract_workflow_v537(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_identity_provider_contract_outputs_v537(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.37 identity-provider contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v537_identity_provider_contract status={summary['overall_status']}")
    print(f"identity_provider_contract_ready={summary['identity_provider_contract_ready']}")
    print(f"oidc_discovery_contract_ready={summary['oidc_discovery_contract_ready']}")
    print(f"jwks_rotation_contract_ready={summary['jwks_rotation_contract_ready']}")
    print(f"identity_validation_matrix_ready={summary['identity_validation_matrix_ready']}")
    print(f"identity_dashboard_access_ready={summary['identity_dashboard_access_ready']}")
    print(f"production_auth_ready={summary['production_auth_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()