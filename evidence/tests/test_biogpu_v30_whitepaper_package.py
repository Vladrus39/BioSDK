from pathlib import Path
import json
from biogpu.paper.package_v30 import build_v30_manifest, write_v30_package

def test_v30_manifest_contains_full_roadmap():
    manifest = build_v30_manifest()
    versions = {c.version for c in manifest.components}
    assert "v2.9" in versions and "v3.0" in versions
    assert len(manifest.claims) >= 7

def test_v30_does_not_claim_gpu_advantage_as_proven():
    manifest = build_v30_manifest()
    gpu_advantage = [c for c in manifest.claims if c.claim_id == "C7_gpu_advantage"]
    assert gpu_advantage
    assert gpu_advantage[0].current_status in {"planned", "requires_live_lab", "requires_power_pc"}

def test_v30_live_claim_requires_lab():
    manifest = build_v30_manifest()
    live = [c for c in manifest.claims if c.claim_id == "C6_live_biogpu_prototype"][0]
    assert live.current_status == "requires_live_lab"
    assert "qualified" in live.required_next_evidence.lower()

def test_v30_package_writes_outputs(tmp_path: Path):
    summary = write_v30_package(tmp_path, tmp_path)
    assert summary["component_count"] >= 15
    assert summary["gpu_advantage_claim_proven"] is False
    assert (tmp_path / "v30_manifest.json").exists()
    assert (tmp_path / "v30_claim_ladder.csv").exists()
    assert (tmp_path / "paper" / "BIOGPU_CORE_WHITEPAPER.md").exists()
    data = json.loads((tmp_path / "v30_manifest.json").read_text(encoding="utf-8"))
    assert data["version"] == "v3.0"
