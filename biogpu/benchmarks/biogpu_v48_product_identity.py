"""Generate v4.8 product identity, NSI draft and OS roadmap artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from biogpu.product.identity_v48 import product_identity, assert_identity_consistent
from biogpu.standards.nsi_v10 import nsi_spec, assert_nsi_minimum_complete


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run(out_dir: str = "outputs/v48_product_identity") -> dict:
    assert_identity_consistent()
    assert_nsi_minimum_complete()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    identity = product_identity()
    nsi = nsi_spec()
    summary = {
        "version": "4.8",
        "repository_name_kept": True,
        "repository_name": "BioGPU-Core",
        "primary_external_name": "BioCompute Runtime",
        "sdk_layer": "BioSDK / Living Compute SDK",
        "standard_draft": "NSI-1.0 / Neural Substrate Interface",
        "long_term_goal": "BioCompute OS",
        "gpu_replacement_claim": False,
        "nsi_schema_count": len(nsi["schemas"]),
        "roadmap_stage_count": len(identity["roadmap"]),
    }
    write_json(out / "product_identity_v48.json", identity)
    write_json(out / "nsi_1_0_draft_spec.json", nsi)
    write_json(out / "v48_summary.json", summary)
    (out / "BIOGPU_V48_PRODUCT_IDENTITY_REPORT.md").write_text(
        "# BioGPU-Core v4.8 Product Identity Report\n\n"
        "BioGPU-Core remains the technical kernel and project codename.\n\n"
        "Primary external product: **BioCompute Runtime**.\n\n"
        "Developer layer: **BioSDK / Living Compute SDK**.\n\n"
        "Interface draft: **NSI-1.0 / Neural Substrate Interface**.\n\n"
        "Long-term commercial target: **BioCompute OS**.\n\n"
        "The project must not be marketed as a direct GPU/CUDA/LLM accelerator replacement until live evidence proves a narrow advantage.\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
