from __future__ import annotations

import json
from pathlib import Path

import h5py

from biogpu.benchmarks.biogpu_v524_external_export_validation import run
from biogpu.sdk.external_export_validation_v524 import build_external_export_validation_gate_v524, validate_external_export_sample_v524, write_external_export_validation_outputs_v524


def _write_minimal_mcs_hdf5(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as handle:
        handle.attrs["McsHdf5ProtocolType"] = "RawData"
        handle.attrs["McsHdf5ProtocolVersion"] = 1
        stream = handle.create_group("Data/Recording_0/AnalogStream/Stream_0")
        stream.create_dataset("ChannelData", data=[[1, 2, 3, 4], [5, 6, 7, 8]])
        stream.create_dataset("ChannelDataTimeStamps", data=[[0, 4, 1]])
        event_stream = handle.create_group("Data/Recording_0/EventStream/Stream_0")
        event_stream.create_dataset("EventEntity_0", data=[[1, 2], [0, 0]])


def test_v524_validates_mcs_hdf5_readonly_export(tmp_path):
    path = tmp_path / "data" / "external" / "api_exports" / "mcs_mea2100" / "sample.h5"
    _write_minimal_mcs_hdf5(path)

    result = validate_external_export_sample_v524(path, tmp_path)
    report = result["report"]

    assert report["gate_status"] == "readonly_external_export_validated"
    assert report["file_format"] == "mcs_hdf5_rawdata"
    assert report["safety_scan_passed"] is True
    assert report["readonly_data_evidence"] is True
    assert report["root_attrs"]["McsHdf5ProtocolType"] == "RawData"


def test_v524_blocks_live_control_json(tmp_path):
    path = tmp_path / "data" / "external" / "api_exports" / "finalspark" / "unsafe.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mode": "read_only", "stimulation_pattern": {"pulse_width": 10}}), encoding="utf-8")

    report = validate_external_export_sample_v524(path, tmp_path)["report"]

    assert report["gate_status"] == "blocked_live_control_terms_detected"
    assert report["safety_scan_passed"] is False
    assert report["forbidden_hits"]


def test_v524_gate_counts_validated_exports(tmp_path):
    _write_minimal_mcs_hdf5(tmp_path / "data" / "external" / "api_exports" / "mcs_mea2100" / "sample.h5")

    gate = build_external_export_validation_gate_v524(tmp_path)

    assert gate["overall_status"] == "real_external_readonly_export_validated"
    assert gate["candidate_export_count"] == 1
    assert gate["validated_export_count"] == 1
    assert gate["real_external_ready"] is True
    assert gate["bic_os_phase_locked"] is True


def test_v524_write_outputs(tmp_path):
    _write_minimal_mcs_hdf5(tmp_path / "data" / "external" / "api_exports" / "mcs_mea2100" / "sample.h5")
    gate = build_external_export_validation_gate_v524(tmp_path)

    paths = write_external_export_validation_outputs_v524(gate, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["reports_json"]).exists()
    assert Path(paths["reports_csv"]).exists()
    assert "External Export Validation" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v524_runner_writes_summary(tmp_path):
    _write_minimal_mcs_hdf5(tmp_path / "data" / "external" / "api_exports" / "mcs_mea2100" / "sample.h5")

    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["real_external_ready"] is True
    assert (tmp_path / "out" / "V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json").exists()