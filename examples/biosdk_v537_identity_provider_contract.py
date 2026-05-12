from __future__ import annotations

from pathlib import Path

from biogpu.runtime.identity_provider_contract_v537 import run_identity_provider_contract_workflow_v537, write_identity_provider_contract_outputs_v537


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v537_identity_provider_contract_example"
    audit = run_identity_provider_contract_workflow_v537(root, out)
    write_identity_provider_contract_outputs_v537(audit, out)
    print(audit["overall_status"])
    print(f"identity_provider_contract_ready={audit['identity_provider_contract_ready']}")
    print(f"production_auth_ready={audit['production_auth_ready']}")
    print(f"real_idp_config_found={audit['direct_answer']['did_we_find_real_identity_provider_config']}")


if __name__ == "__main__":
    main()