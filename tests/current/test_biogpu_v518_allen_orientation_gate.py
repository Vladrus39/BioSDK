from __future__ import annotations

import json
from pathlib import Path

from biogpu.benchmarks.biogpu_v518_allen_orientation_gate import run
from biogpu.sdk.allen_orientation_v518 import build_allen_orientation_gate_v518, orientation_candidate_signals_v518, write_allen_orientation_outputs_v518


def test_v518_missing_allen_sample_is_honest_gate(tmp_path):
    gate = build_allen_orientation_gate_v518(tmp_path)

    assert gate["overall_status"] == "allen_orientation_sample_missing_download_required"
    assert gate["nwb_sample_count"] == 0
    assert gate["validated_sample_count"] == 0
    assert gate["bic_os_phase_locked"] is True


def test_v518_manifest_present_needs_nwb_download(tmp_path):
    manifest = tmp_path / "data" / "external" / "allen" / "session_manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"session_id": "placeholder", "stimulus": "drifting_gratings"}), encoding="utf-8")

    gate = build_allen_orientation_gate_v518(tmp_path)

    assert gate["overall_status"] == "allen_manifest_present_needs_nwb_download"
    assert gate["manifest_asset_count"] == 1
    assert gate["validated_sample_count"] == 0


def test_v518_orientation_signal_detection_prefers_stimulus_metadata():
    candidates = [
        {"path": "/intervals/trials", "kind": "interval_table", "keys": ["start_time", "stop_time"]},
        {"path": "/stimulus/presentation", "kind": "table", "keys": ["stimulus_name", "orientation"]},
    ]

    signals = orientation_candidate_signals_v518(candidates)

    assert signals == ["/stimulus/presentation"]


def test_v518_write_outputs(tmp_path):
    paths = write_allen_orientation_outputs_v518(tmp_path, tmp_path / "out")

    summary_path = Path(paths["summary_json"])

    assert summary_path.exists()
    assert Path(paths["download_plan_json"]).exists()
    assert Path(paths["asset_manifest_csv"]).exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["overall_status"] == "allen_orientation_sample_missing_download_required"


def test_v518_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["overall_status"] == "allen_orientation_sample_missing_download_required"
    assert (tmp_path / "out" / "V518_ALLEN_ORIENTATION_GATE_SUMMARY.json").exists()
