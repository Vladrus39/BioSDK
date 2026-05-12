"""Runner for BioGPU-Core v5.44 private registry handoff contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.private_registry_handoff_v544 import DEFAULT_OUT, run_private_registry_handoff_workflow_v544, write_private_registry_handoff_outputs_v544


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_private_registry_handoff_workflow_v544(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_private_registry_handoff_outputs_v544(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.44 private registry handoff contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v544_private_registry_handoff status={summary['overall_status']}")
    print(f"private_registry_handoff_contract_ready={summary['private_registry_handoff_contract_ready']}")
    print(f"v543_dependency_ready={summary['v543_dependency_ready']}")
    print(f"local_handoff_package_ready={summary['local_handoff_package_ready']}")
    print(f"handoff_access_matrix_ready={summary['handoff_access_matrix_ready']}")
    print(f"handoff_revocation_probe_ready={summary['handoff_revocation_probe_ready']}")
    print(f"local_registry_index_ready={summary['local_registry_index_ready']}")
    print(f"live_private_registry_ready={summary['live_private_registry_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()