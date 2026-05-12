from __future__ import annotations

from pathlib import Path

from biogpu.sdk.private_beta_onboarding_v540 import run_private_beta_onboarding_contract_workflow_v540, write_private_beta_onboarding_outputs_v540


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v540_private_beta_onboarding_example"
    audit = run_private_beta_onboarding_contract_workflow_v540(root, out)
    write_private_beta_onboarding_outputs_v540(audit, out)
    print(audit["overall_status"])
    print(f"private_beta_onboarding_contract_ready={audit['private_beta_onboarding_contract_ready']}")
    print(f"external_beta_ready={audit['external_beta_ready']}")
    print(f"full_biosdk_ready={audit['full_biosdk_ready']}")


if __name__ == "__main__":
    main()