from __future__ import annotations

import json
import zipfile
from pathlib import Path

from biogpu.integration.e2e_v31 import E2EConfigV31, build_manifest_v31, pattern_to_replay_observation_v31, run_e2e_v31
from biogpu.encoding.base_v26 import EncoderInput
from biogpu.encoding.registry_v26 import encode_with_registry_v26
from biogpu.runtime.session_manager_v24 import validate_manifest


def test_v31_manifest_validates_for_replay():
    manifest = build_manifest_v31(E2EConfigV31())
    assert validate_manifest(manifest) == []
    assert manifest.config["v31_e2e"]["live_output_performed"] is False


def test_v31_pattern_to_observation_has_features():
    pattern = encode_with_registry_v26("spatial_v26", EncoderInput("demo", [0, 1, 2, 3]))
    obs = pattern_to_replay_observation_v31(pattern)
    assert len(obs.features) == len(obs.feature_names)
    assert obs.metadata["replay_substrate"] == "deterministic_v31_feature_projection"


def test_v31_full_run_creates_bundle(tmp_path: Path):
    summary = run_e2e_v31(tmp_path, E2EConfigV31())
    assert summary.success is True
    assert summary.prediction == "target_response"
    assert (tmp_path / "e2e_summary_v31.json").exists()
    assert (tmp_path / summary.result_bundle).exists()
    with zipfile.ZipFile(tmp_path / summary.result_bundle) as z:
        names = set(z.namelist())
    assert "run_manifest_v31.json" in names
    assert "BIOGPU_V31_E2E_REPORT.md" in names


def test_v31_summary_keeps_claim_boundaries(tmp_path: Path):
    run_e2e_v31(tmp_path, E2EConfigV31())
    data = json.loads((tmp_path / "e2e_summary_v31.json").read_text(encoding="utf-8"))
    assert "no GPU advantage claim" in data["safety_boundary"]
    assert data["run_mode"] == "replay"
