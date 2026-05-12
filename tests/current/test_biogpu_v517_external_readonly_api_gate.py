from __future__ import annotations

import json
from pathlib import Path

import h5py

from biogpu.benchmarks.biogpu_v517_external_readonly_api_gate import run
from biogpu.sdk.external_readonly_v517 import TOKEN_ENV_BY_PLATFORM, build_external_readonly_api_gate_v517, validate_mock_readonly_platform_v517, write_external_readonly_outputs_v517


def _clear_partner_tokens(monkeypatch):
    for env_name in TOKEN_ENV_BY_PLATFORM.values():
        monkeypatch.delenv(env_name, raising=False)


def _write_minimal_mcs_hdf5(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as handle:
        handle.attrs["McsHdf5ProtocolType"] = "RawData"
        handle.attrs["McsHdf5ProtocolVersion"] = 1
        stream = handle.create_group("Data/Recording_0/AnalogStream/Stream_0")
        stream.create_dataset("ChannelData", data=[[1, 2, 3], [4, 5, 6]])


def test_v517_validates_finalspark_mock_readonly_contract():
    result = validate_mock_readonly_platform_v517("finalspark_remote_wetware")
    report = result["report"]

    assert report["contract_status"] == "mock_readonly_contract_passed"
    assert report["spike_event_count"] > 0
    assert report["trace_sample_count"] > 0
    assert report["supports_live_stimulation"] is False
    assert report["write_denial_passed"] is True
    assert result["trace_fixture"]["safety"]["live_output_performed"] is False


def test_v517_all_mock_contracts_pass_but_real_external_stays_required(tmp_path, monkeypatch):
    _clear_partner_tokens(monkeypatch)

    gate = build_external_readonly_api_gate_v517(tmp_path)

    assert gate["overall_status"] == "mock_readonly_contract_passed_real_external_required"
    assert gate["mock_contract_passed_count"] == gate["platform_count"]
    assert gate["real_external_ready"] is False
    assert gate["bic_os_phase_locked"] is True


def test_v517_detects_non_secret_export_presence_without_claiming_ready(tmp_path, monkeypatch):
    _clear_partner_tokens(monkeypatch)

    export_path = tmp_path / "data" / "external" / "api_exports" / "sample.json"
    export_path.parent.mkdir(parents=True)
    export_path.write_text(json.dumps({"kind": "read_only_export_fixture"}), encoding="utf-8")

    gate = build_external_readonly_api_gate_v517(tmp_path)

    assert gate["overall_status"] == "mock_readonly_contract_passed_real_material_needs_validation"
    assert gate["real_export_file_count"] == 1
    assert gate["real_external_ready"] is False


def test_v517_uses_v524_validated_export_for_real_ready(tmp_path, monkeypatch):
    _clear_partner_tokens(monkeypatch)
    _write_minimal_mcs_hdf5(tmp_path / "data" / "external" / "api_exports" / "mcs_mea2100" / "sample.h5")

    gate = build_external_readonly_api_gate_v517(tmp_path)

    assert gate["overall_status"] == "real_external_readonly_export_validated"
    assert gate["real_external_ready"] is True
    assert gate["validated_real_export_count"] == 1


def test_v517_write_outputs(tmp_path):
    paths = write_external_readonly_outputs_v517(tmp_path, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["platform_reports_csv"]).exists()
    assert Path(paths["trace_fixtures_json"]).exists()
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    assert summary["platform_count"] >= 4


def test_v517_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["all_mock_contracts_passed"] is True
    assert result["summary"]["real_external_ready"] is False
    assert (tmp_path / "out" / "V517_EXTERNAL_READONLY_API_SUMMARY.json").exists()
