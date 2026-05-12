from pathlib import Path

from biogpu.os.differentiation_v50 import differentiators, os_capabilities, proof_targets, PROJECT_POSITIONING
from biogpu.benchmarks.biogpu_v50_differentiation_roadmap import build_report


def test_positioning_has_bic_os_and_no_gpu_replacement_claim():
    assert PROJECT_POSITIONING["technical_kernel"] == "BioGPU-Core"
    assert PROJECT_POSITIONING["os_codename"] == "BiC OS"
    assert "vendor-neutral" in PROJECT_POSITIONING["primary_claim"].lower()


def test_differentiators_cover_required_themes():
    titles = " ".join(d.title.lower() for d in differentiators())
    assert "vendor-neutral" in titles
    assert "evidence" in titles
    assert "llm" in titles
    assert "safety" in titles
    assert len(differentiators()) >= 8


def test_os_capabilities_and_proof_targets_are_nonempty():
    assert len(os_capabilities()) >= 7
    assert len(proof_targets()) >= 6
    assert any(p.can_prove_before_lab for p in proof_targets())
    assert any(not p.can_prove_before_lab for p in proof_targets())


def test_report_generation(tmp_path: Path):
    result = build_report(tmp_path)
    assert result["ready"] is True
    assert (tmp_path / "BIOGPU_V50_DIFFERENTIATION_REPORT.md").exists()
    assert (tmp_path / "v50_differentiators.csv").exists()
    assert (tmp_path / "v50_proof_targets.csv").exists()
