"""Generate BioGPU-Core v4.9 naming, competitive and BiC OS strategy artifacts."""
from __future__ import annotations

import json
from pathlib import Path

from biogpu.product.identity_v49 import product_identity_v49, assert_identity_v49_consistent
from biogpu.os.blueprint_v49 import bic_os_blueprint, assert_bic_os_blueprint_complete
from biogpu.standards.nsi_v10 import nsi_spec, assert_nsi_minimum_complete


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run(out_dir: str = "outputs/v49_naming_os_strategy") -> dict:
    assert_identity_v49_consistent()
    assert_bic_os_blueprint_complete()
    assert_nsi_minimum_complete()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    identity = product_identity_v49()
    blueprint = bic_os_blueprint()
    nsi = nsi_spec()
    summary = {
        "version": "4.9",
        "repository_name": identity["repository_name"],
        "near_term_product": identity["near_term_product"],
        "sdk_layer": identity["sdk_layer"],
        "standard": identity["standard"],
        "os_working_codename": identity["os_working_codename"],
        "somaos_primary_brand": False,
        "gpu_replacement_claim": False,
        "vendor_neutral_runtime_claim": True,
        "os_module_count": len(blueprint["modules"]),
        "llm_workflow_count": len(blueprint["llm_workflows"]),
        "first_mover_axis_count": len(blueprint["first_mover_axes"]),
        "nsi_schema_count": len(nsi["schemas"]),
        "ready_for_power_pc_handoff": True,
    }
    write_json(out / "product_identity_v49.json", identity)
    write_json(out / "bic_os_blueprint_v49.json", blueprint)
    write_json(out / "nsi_1_0_draft_spec_v49_reference.json", nsi)
    write_json(out / "v49_summary.json", summary)
    (out / "BIOGPU_V49_NAMING_OS_STRATEGY_REPORT.md").write_text(
        "# BioGPU-Core v4.9 Naming + BiC OS Strategy Report\n\n"
        "BioGPU-Core remains the technical kernel. The near-term external product is BioCompute Runtime, "
        "with BioSDK / Living Compute SDK as the developer layer and NSI-1.0 as the interface standard.\n\n"
        "SomaOS is not recommended as the primary public brand due to name collision risk.\n\n"
        "BiC OS is introduced as a short working codename for the future BioCompute OS / Biological Interface Compute OS. "
        "It is not legally cleared and should remain a codename until trademark/domain/package checks are completed.\n\n"
        "The strongest differentiator is not claiming first biological OS. It is building a vendor-neutral runtime/interface "
        "layer for living neural compute, LLM agents, replay datasets, wetware APIs, safety, experiments and auditable result bundles.\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
