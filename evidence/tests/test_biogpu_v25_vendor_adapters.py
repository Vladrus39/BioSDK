from pathlib import Path

import pytest

from biogpu.substrates.vendor_registry_v25 import (
    build_safe_probe_command,
    build_v25_capability_matrix,
    build_v25_vendor_adapters,
    run_v25_dry_run,
)
from biogpu.substrates.vendors import BioGPUVendorCommand, UnsafeVendorCommandError


def test_v25_vendor_registry_contains_four_adapter_classes():
    adapters = build_v25_vendor_adapters()
    ids = {a.adapter_id for a in adapters}
    assert "mcs_mea2100_class" in ids
    assert "axion_maestro_class" in ids
    assert "threebrain_hdmea_class" in ids
    assert "finalspark_remote_wetware_class" in ids


def test_v25_capability_matrix_has_recording_and_boundary_notice():
    matrix = build_v25_capability_matrix()
    assert len(matrix) == 4
    assert all(row["recording_supported"] for row in matrix)
    assert all("No" in row["boundary_notice"] for row in matrix)


def test_v25_safe_probe_command_is_accepted_in_dry_run():
    adapter = build_v25_vendor_adapters()[0]
    adapter.connect()
    ack = adapter.send_stimulation_pattern(build_safe_probe_command())
    assert ack["accepted"] is True
    assert ack["live_output_performed"] is False


def test_v25_unsafe_live_fields_are_rejected():
    adapter = build_v25_vendor_adapters()[0]
    bad = BioGPUVendorCommand(
        command_id="bad",
        benchmark_id="B0_target_vs_random_electrode",
        pattern_id="unsafe",
        electrode_group_aliases=["target_group_A"],
        payload={"voltage": "not allowed in repository"},
    )
    with pytest.raises(UnsafeVendorCommandError):
        adapter.send_stimulation_pattern(bad)


def test_v25_numeric_channel_alias_is_rejected():
    adapter = build_v25_vendor_adapters()[0]
    bad = BioGPUVendorCommand(
        command_id="bad_numeric",
        benchmark_id="B0_target_vs_random_electrode",
        pattern_id="unsafe_numeric",
        electrode_group_aliases=["12"],
    )
    with pytest.raises(UnsafeVendorCommandError):
        adapter.send_stimulation_pattern(bad)


def test_v25_vendor_backend_required_blocks_connect():
    adapter = build_v25_vendor_adapters(mode="vendor_backend_required")[0]
    with pytest.raises(NotImplementedError):
        adapter.connect()


def test_v25_dry_run_writes_outputs(tmp_path: Path):
    summary = run_v25_dry_run(tmp_path)
    assert summary["adapter_count"] == 4
    assert summary["live_output_performed"] is False
    assert (tmp_path / "v25_vendor_capability_matrix.json").exists()
    assert (tmp_path / "v25_vendor_capability_matrix.csv").exists()
    assert (tmp_path / "BIOGPU_V25_VENDOR_ADAPTERS_REPORT.md").exists()
