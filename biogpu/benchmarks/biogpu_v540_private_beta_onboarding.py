"""Runner for BioGPU-Core v5.40 private beta onboarding contract proof."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from biogpu.sdk.private_beta_onboarding_v540 import DEFAULT_OUT, run_private_beta_onboarding_contract_workflow_v540, write_private_beta_onboarding_outputs_v540


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_private_beta_onboarding_contract_workflow_v540(root, out_dir)
    resolved_out = Path(root) / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_private_beta_onboarding_outputs_v540(audit, resolved_out)
    return {"summary": audit, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BioGPU-Core v5.40 private beta onboarding contract proof.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()
    result = run(args.root, args.out_dir)
    summary = result["summary"]
    print(f"v540_private_beta_onboarding status={summary['overall_status']}")
    print(f"private_beta_onboarding_contract_ready={summary['private_beta_onboarding_contract_ready']}")
    print(f"v539_dependency_ready={summary['v539_dependency_ready']}")
    print(f"release_operations_contract_ready={summary['release_operations_contract_ready']}")
    print(f"participant_gate_ready={summary['participant_gate_ready']}")
    print(f"external_beta_ready={summary['external_beta_ready']}")
    print(f"full_biosdk_ready={summary['full_biosdk_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()