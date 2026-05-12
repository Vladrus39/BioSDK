from pathlib import Path

from biogpu.hardware.blueprint_v22 import (
    build_biogpu_a1_hardware_blueprint_v22,
    write_v22_outputs,
)


def test_v22_blueprint_has_core_components():
    bp = build_biogpu_a1_hardware_blueprint_v22()
    ids = {c.id for c in bp.components}
    required = {
        "wet_cartridge",
        "mea_chip",
        "headstage_stimulator",
        "environment_control",
        "host_pc",
        "runtime",
        "storage",
        "sop_safety",
    }
    assert required.issubset(ids)


def test_v22_connections_cover_runtime_mea_living_path():
    bp = build_biogpu_a1_hardware_blueprint_v22()
    edges = {(c.source, c.target) for c in bp.connections}
    assert ("runtime", "headstage_stimulator") in edges
    assert ("headstage_stimulator", "mea_chip") in edges
    assert ("mea_chip", "wet_cartridge") in edges
    assert ("wet_cartridge", "mea_chip") in edges
    assert ("headstage_stimulator", "runtime") in edges


def test_v22_formulas_include_energy_and_storage():
    bp = build_biogpu_a1_hardware_blueprint_v22()
    formulas = {f.id for f in bp.formulas}
    assert "energy_per_task" in formulas
    assert "storage_per_day" in formulas
    assert "loop_latency" in formulas


def test_v22_outputs_are_written(tmp_path: Path):
    summary = write_v22_outputs(tmp_path)
    assert summary["components"] >= 10
    assert (tmp_path / "biogpu_a1_hardware_blueprint.json").exists()
    assert (tmp_path / "BIOGPU_A1_HARDWARE_REPORT.md").exists()
    assert (tmp_path / "BIOGPU_A1_CONNECTION_TABLE.csv").exists()
    assert (tmp_path / "BIOGPU_A1_BOM.csv").exists()
