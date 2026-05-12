from biogpu.product.identity_v49 import product_identity_v49, assert_identity_v49_consistent
from biogpu.os.blueprint_v49 import bic_os_blueprint, assert_bic_os_blueprint_complete
from biogpu.benchmarks.biogpu_v49_naming_os_strategy import run


def test_identity_v49_keeps_biogpu_core_and_adds_bic_os():
    data = product_identity_v49()
    assert data["repository_name"] == "BioGPU-Core"
    assert data["os_working_codename"] == "BiC OS"
    assert data["near_term_product"] == "BioCompute Runtime"
    assert any(n["name"] == "SomaOS" and "do not use" in n["decision"] for n in data["name_decisions"])
    assert_identity_v49_consistent()


def test_bic_os_blueprint_has_llm_and_safety_modules():
    data = bic_os_blueprint()
    names = {m["name"] for m in data["modules"]}
    assert "LLM/Agent Bridge" in names
    assert "Safety Supervisor" in names
    assert "Evidence Ledger" in names
    assert data["default_safety_posture"].startswith("maximum software access")
    assert_bic_os_blueprint_complete()


def test_v49_generator_outputs_strategy(tmp_path):
    summary = run(str(tmp_path))
    assert summary["os_working_codename"] == "BiC OS"
    assert summary["vendor_neutral_runtime_claim"] is True
    assert summary["gpu_replacement_claim"] is False
    assert (tmp_path / "product_identity_v49.json").exists()
    assert (tmp_path / "bic_os_blueprint_v49.json").exists()
    assert (tmp_path / "BIOGPU_V49_NAMING_OS_STRATEGY_REPORT.md").exists()
