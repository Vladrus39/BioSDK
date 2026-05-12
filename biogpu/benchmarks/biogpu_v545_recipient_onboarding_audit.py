"""Runner for BioGPU-Core v5.45 recipient onboarding audit proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.recipient_onboarding_audit_v545 import DEFAULT_OUT, run_recipient_onboarding_audit_workflow_v545, write_recipient_onboarding_audit_outputs_v545


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_recipient_onboarding_audit_workflow_v545(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_recipient_onboarding_audit_outputs_v545(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.45 recipient onboarding audit proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v545_recipient_onboarding_audit status={summary['overall_status']}")
    print(f"recipient_onboarding_audit_contract_ready={summary['recipient_onboarding_audit_contract_ready']}")
    print(f"v544_dependency_ready={summary['v544_dependency_ready']}")
    print(f"recipient_onboarding_matrix_ready={summary['recipient_onboarding_matrix_ready']}")
    print(f"recipient_access_log_ready={summary['recipient_access_log_ready']}")
    print(f"access_expiry_probe_ready={summary['access_expiry_probe_ready']}")
    print(f"real_recipient_onboarding_ready={summary['real_recipient_onboarding_ready']}")
    print(f"live_private_registry_ready={summary['live_private_registry_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()