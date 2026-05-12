from __future__ import annotations

import csv
import json

from biogpu.benchmarks.biogpu_v57_raw_preprocessed_alignment import run
from biogpu.data_ingest.raw_preprocessed_alignment_v57 import (
    build_raw_preprocessed_alignment_report_v57,
    load_preprocessed_pulse_recordings_v57,
    load_raw_event_recordings_v57,
)


RAW_FIELDS = [
    "file",
    "stream",
    "entity",
    "label",
    "detector_kind",
    "event_count",
    "first_timestamp_s",
    "last_timestamp_s",
    "median_interval_s",
    "info_type_values",
    "sample_timestamps_us",
    "candidate_kind",
]

PULSE_FIELDS = [
    "row_index",
    "recording_path",
    "culture",
    "date",
    "condition",
    "target_type",
    "target_id",
    "pulse_index",
    "start_s",
    "end_s",
    "duration_s",
]


def _write_raw_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_pulse_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PULSE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _raw_row(file_name, event_count=3, first=1.0, last=5.0, interval=2.0, kind="light_or_digital_stimulation_event"):
    return {
        "file": file_name,
        "stream": "Stream_0",
        "entity": "EventEntity_0",
        "label": "Digital Event Detector",
        "detector_kind": "digital_port_event",
        "event_count": str(event_count),
        "first_timestamp_s": str(first),
        "last_timestamp_s": str(last),
        "median_interval_s": str(interval),
        "info_type_values": "",
        "sample_timestamps_us": "1000000;3000000;5000000",
        "candidate_kind": kind,
    }


def _pulse_rows(recording_path, target_id="34", starts=(1.0, 3.0, 5.0), condition="lightstim"):
    rows = []
    parts = recording_path.split("/")
    for index, start in enumerate(starts):
        rows.append({
            "row_index": str(index),
            "recording_path": recording_path,
            "culture": parts[-2],
            "date": parts[-3],
            "condition": condition,
            "target_type": "light_spot" if condition == "lightstim" else "stimulation_electrode",
            "target_id": str(target_id),
            "pulse_index": str(index),
            "start_s": str(start),
            "end_s": str(start + 0.02),
            "duration_s": "0.02",
        })
    return rows


def test_v57_loaders_group_raw_entities_and_pulse_rows(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    pulse_csv = tmp_path / "pulse.csv"
    file_name = "11-11-2022\\41438_13DIV\\41438_13DIV_LightStim_Spot34_D-00144.h5"
    _write_raw_csv(raw_csv, [_raw_row(file_name), {**_raw_row(file_name), "entity": "EventEntity_1"}])
    _write_pulse_csv(pulse_csv, _pulse_rows("EXP PTSD/11-11-2022/41438_13DIV/41438_13DIV_LightStim_Spot34_D-00144"))

    raw_recordings = load_raw_event_recordings_v57(raw_csv)
    pulse_recordings = load_preprocessed_pulse_recordings_v57(pulse_csv)

    assert len(raw_recordings) == 1
    assert raw_recordings[0].event_entity_count == 2
    assert raw_recordings[0].representative_event_count == 3
    assert len(pulse_recordings) == 1
    assert pulse_recordings[0].pulse_count == 3
    assert pulse_recordings[0].median_interval_s == 2.0


def test_v57_reports_exact_recording_alignment(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    pulse_csv = tmp_path / "pulse.csv"
    _write_raw_csv(raw_csv, [_raw_row("11-11-2022\\41438_13DIV\\41438_13DIV_LightStim_Spot34_D-00144.h5")])
    _write_pulse_csv(pulse_csv, _pulse_rows("EXP PTSD/11-11-2022/41438_13DIV/41438_13DIV_LightStim_Spot34_D-00144"))

    report = build_raw_preprocessed_alignment_report_v57(raw_csv, pulse_csv)

    assert report.overall_status == "exact_recording_alignment_available"
    assert report.exact_recording_match_count == 1
    assert report.audit_rows[0].match_level == "exact_recording"
    assert report.audit_rows[0].first_event_to_first_pulse_delta_s == 0.0


def test_v57_distinguishes_condition_target_from_exact_alignment(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    pulse_csv = tmp_path / "pulse.csv"
    _write_raw_csv(raw_csv, [_raw_row("12-08-2022\\40617_31DIV\\40617_31DIV_LightStim_Spot55_D-00144.h5")])
    _write_pulse_csv(pulse_csv, _pulse_rows("EXP PTSD/11-11-2022/39566_21DIV/39566_21DIV_LightStim_Spot55_D-00144", target_id="55"))

    report = build_raw_preprocessed_alignment_report_v57(raw_csv, pulse_csv)

    assert report.overall_status == "target_and_temporal_signature_only"
    assert report.exact_recording_match_count == 0
    assert report.condition_target_match_count == 1
    assert report.audit_rows[0].match_level == "condition_target"


def test_v57_reports_temporal_signature_only_when_target_differs(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    pulse_csv = tmp_path / "pulse.csv"
    _write_raw_csv(raw_csv, [_raw_row("12-08-2022\\40617_31DIV\\40617_31DIV_LightStim_Spot67_D-00144.h5")])
    _write_pulse_csv(pulse_csv, _pulse_rows("EXP PTSD/11-11-2022/39566_21DIV/39566_21DIV_LightStim_Spot34_D-00144", target_id="34"))

    report = build_raw_preprocessed_alignment_report_v57(raw_csv, pulse_csv)

    assert report.overall_status == "class_temporal_signature_only"
    assert report.temporal_signature_match_count == 1
    assert report.audit_rows[0].match_level == "temporal_signature"


def test_v57_missing_inputs_are_explicit(tmp_path):
    report = build_raw_preprocessed_alignment_report_v57(tmp_path / "missing_raw.csv", tmp_path / "missing_pulse.csv")
    assert report.overall_status == "missing_inputs"
    assert report.raw_event_recording_count == 0
    assert report.preprocessed_pulse_recording_count == 0


def test_v57_runner_writes_outputs(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    pulse_csv = tmp_path / "pulse.csv"
    _write_raw_csv(raw_csv, [_raw_row("11-11-2022\\41438_13DIV\\41438_13DIV_LightStim_Spot34_D-00144.h5")])
    _write_pulse_csv(pulse_csv, _pulse_rows("EXP PTSD/11-11-2022/41438_13DIV/41438_13DIV_LightStim_Spot34_D-00144"))

    result = run(raw_event_csv=raw_csv, pulse_metadata_csv=pulse_csv, out_dir=tmp_path / "out", ensure_v56=False)
    summary = result["summary"]

    assert summary["overall_status"] == "exact_recording_alignment_available"
    assert (tmp_path / "out" / "V57_RAW_PREPROCESSED_ALIGNMENT_AUDIT.csv").exists()
    loaded = json.loads((tmp_path / "out" / "V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json").read_text(encoding="utf-8"))
    assert loaded["exact_recording_match_count"] == 1
