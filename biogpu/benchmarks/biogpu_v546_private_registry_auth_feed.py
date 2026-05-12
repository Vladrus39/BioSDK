"""Runner for BioGPU-Core v5.46 private registry auth/feed proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.private_registry_auth_feed_v546 import DEFAULT_OUT, run_private_registry_auth_feed_workflow_v546, write_private_registry_auth_feed_outputs_v546


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_private_registry_auth_feed_workflow_v546(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_private_registry_auth_feed_outputs_v546(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.46 private registry auth/feed proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v546_private_registry_auth_feed status={summary['overall_status']}")
    print(f"private_registry_auth_feed_contract_ready={summary['private_registry_auth_feed_contract_ready']}")
    print(f"v545_dependency_ready={summary['v545_dependency_ready']}")
    print(f"auth_feed_matrix_ready={summary['auth_feed_matrix_ready']}")
    print(f"expiring_feed_manifest_ready={summary['expiring_feed_manifest_ready']}")
    print(f"expiring_feed_probe_ready={summary['expiring_feed_probe_ready']}")
    print(f"registry_log_export_contract_ready={summary['registry_log_export_contract_ready']}")
    print(f"real_private_registry_auth_ready={summary['real_private_registry_auth_ready']}")
    print(f"live_private_registry_ready={summary['live_private_registry_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()