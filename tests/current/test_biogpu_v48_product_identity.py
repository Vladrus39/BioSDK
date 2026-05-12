from pathlib import Path

from biogpu.product.identity_v48 import product_identity, assert_identity_consistent
from biogpu.standards.nsi_v10 import nsi_spec, assert_nsi_minimum_complete
from biogpu.benchmarks.biogpu_v48_product_identity import run


def test_product_identity_keeps_biogpu_core_name():
    data = product_identity()
    assert data["keep_repository_name"] == "BioGPU-Core"
    assert data["primary_external_name"] == "BioCompute Runtime"
    assert data["long_term_goal"] == "BioCompute OS"
    assert data["gpu_claim_policy"]
    assert_identity_consistent()


def test_nsi_draft_has_core_schemas():
    data = nsi_spec()
    names = {schema["name"] for schema in data["schemas"]}
    assert "BioComputeTrace" in names
    assert "BioComputeTaskManifest" in names
    assert "BioComputeResultBundle" in names
    assert "BioComputeAdapterContract" in names
    assert data["blocked_by_default"]
    assert_nsi_minimum_complete()


def test_v48_generator_outputs_files(tmp_path):
    summary = run(str(tmp_path))
    assert summary["repository_name"] == "BioGPU-Core"
    assert summary["nsi_schema_count"] >= 7
    assert (tmp_path / "product_identity_v48.json").exists()
    assert (tmp_path / "nsi_1_0_draft_spec.json").exists()
    assert (tmp_path / "BIOGPU_V48_PRODUCT_IDENTITY_REPORT.md").exists()
