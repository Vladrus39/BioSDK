"""Runner for BioGPU-Core v5.47 registry revoke/yank notification proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.registry_revoke_yank_notification_v547 import DEFAULT_OUT, run_registry_revoke_yank_notification_workflow_v547, write_registry_revoke_yank_notification_outputs_v547


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_registry_revoke_yank_notification_workflow_v547(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_registry_revoke_yank_notification_outputs_v547(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.47 registry revoke/yank notification proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v547_registry_revoke_yank_notification status={summary['overall_status']}")
    print(f"registry_revoke_yank_notification_contract_ready={summary['registry_revoke_yank_notification_contract_ready']}")
    print(f"v546_dependency_ready={summary['v546_dependency_ready']}")
    print(f"revoke_yank_matrix_ready={summary['revoke_yank_matrix_ready']}")
    print(f"local_yank_manifest_ready={summary['local_yank_manifest_ready']}")
    print(f"recipient_notification_ack_trail_ready={summary['recipient_notification_ack_trail_ready']}")
    print(f"revoke_yank_effect_probe_ready={summary['revoke_yank_effect_probe_ready']}")
    print(f"incident_linkage_export_ready={summary['incident_linkage_export_ready']}")
    print(f"production_yank_ready={summary['production_yank_ready']}")
    print(f"live_private_registry_ready={summary['live_private_registry_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()