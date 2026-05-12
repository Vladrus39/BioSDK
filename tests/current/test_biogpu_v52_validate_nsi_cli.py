from __future__ import annotations

import json

from biogpu.standards.nsi_cli_v52 import main as validate_nsi_main
from biogpu.standards.nsi_v10 import reference_nsi_objects


def test_validate_nsi_cli_lists_schemas(capsys):
    code = validate_nsi_main(["--list-schemas"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert "BioComputeTrace" in out["schemas"]
    assert out["standard"] == "NSI-1.0"


def test_validate_nsi_cli_accepts_reference_trace(tmp_path, capsys):
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(reference_nsi_objects()["BioComputeTrace"]), encoding="utf-8")
    code = validate_nsi_main(["--schema", "BioComputeTrace", "--input", str(path)])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["valid"] is True
    assert out["schema_name"] == "BioComputeTrace"


def test_validate_nsi_cli_returns_nonzero_for_invalid_payload(tmp_path, capsys):
    path = tmp_path / "trace.json"
    payload = dict(reference_nsi_objects()["BioComputeTrace"])
    payload.pop("checksum")
    path.write_text(json.dumps(payload), encoding="utf-8")
    code = validate_nsi_main(["--schema", "BioComputeTrace", "--input", str(path)])
    out = json.loads(capsys.readouterr().out)
    assert code == 1
    assert out["valid"] is False
    assert any(issue["path"] == "checksum" for issue in out["issues"])


def test_validate_nsi_cli_writes_report(tmp_path, capsys):
    payload_path = tmp_path / "bundle.json"
    report_path = tmp_path / "report.json"
    payload_path.write_text(json.dumps(reference_nsi_objects()["BioComputeResultBundle"]), encoding="utf-8")
    code = validate_nsi_main([
        "--schema",
        "BioComputeResultBundle",
        "--input",
        str(payload_path),
        "--output",
        str(report_path),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["valid"] is True
    assert report_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["valid"] is True


def test_validate_nsi_cli_writes_reference_objects(tmp_path, capsys):
    code = validate_nsi_main(["--write-reference", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["count"] >= 8
    assert (tmp_path / "NSI_1_0_REFERENCE_OBJECTS.json").exists()
    assert (tmp_path / "BioComputeTrace.reference.json").exists()


def test_existing_biogpu_cli_exposes_validate_nsi(tmp_path, capsys):
    from biogpu.cli import main as biogpu_cli_main

    path = tmp_path / "safety.json"
    path.write_text(json.dumps(reference_nsi_objects()["BioComputeSafetyProfile"]), encoding="utf-8")
    code = biogpu_cli_main(["validate-nsi", "--schema", "BioComputeSafetyProfile", "--input", str(path)])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["valid"] is True