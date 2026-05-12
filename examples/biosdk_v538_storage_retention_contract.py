from __future__ import annotations

from pathlib import Path

from biogpu.runtime.storage_retention_v538 import run_storage_retention_contract_workflow_v538, write_storage_retention_contract_outputs_v538


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v538_storage_retention_contract_example"
    audit = run_storage_retention_contract_workflow_v538(root, out)
    write_storage_retention_contract_outputs_v538(audit, out)
    print(audit["overall_status"])
    print(f"storage_retention_contract_ready={audit['storage_retention_contract_ready']}")
    print(f"production_object_storage_ready={audit['production_object_storage_ready']}")
    print(f"real_storage_config_found={audit['direct_answer']['did_we_find_real_object_storage_config']}")


if __name__ == "__main__":
    main()