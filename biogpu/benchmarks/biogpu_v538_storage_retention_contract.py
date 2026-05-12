"""Runner for BioGPU-Core v5.38 storage retention contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.runtime.storage_retention_v538 import DEFAULT_OUT, run_storage_retention_contract_workflow_v538, write_storage_retention_contract_outputs_v538


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_storage_retention_contract_workflow_v538(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_storage_retention_contract_outputs_v538(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.38 storage retention contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v538_storage_retention_contract status={summary['overall_status']}")
    print(f"storage_retention_contract_ready={summary['storage_retention_contract_ready']}")
    print(f"storage_object_integrity_ready={summary['storage_object_integrity_ready']}")
    print(f"retention_manifest_ready={summary['retention_manifest_ready']}")
    print(f"immutable_overwrite_denial_ready={summary['immutable_overwrite_denial_ready']}")
    print(f"production_object_storage_ready={summary['production_object_storage_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()