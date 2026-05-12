from __future__ import annotations
import pytest

from biogpu.apis import list_external_api_platforms_v37, make_external_api_client_v37, PermissionDeniedV37, commercial_tiers_v37
from biogpu.benchmarks.biogpu_v37_external_api_integration import generate_report_v37


def test_v37_lists_four_platforms():
    platforms = list_external_api_platforms_v37()
    assert platforms == sorted(platforms)
    assert len(platforms) == 4
    assert "finalspark_remote_wetware" in platforms
    assert "threebrain_hdmea" in platforms


def test_v37_read_only_clients_export_trace():
    for platform in list_external_api_platforms_v37():
        client = make_external_api_client_v37(platform, "read_only")
        meta = client.connect()
        assert meta.connected is True
        assert meta.supports_live_stimulation is False
        trace = client.export_biogpu_trace(duration_s=0.25)
        assert trace.platform == platform
        assert len(trace.spike_events) > 0
        assert trace.safety["live_output_performed"] is False


def test_v37_write_is_denied_even_for_abstract_payload():
    client = make_external_api_client_v37("mcs_mea2100", "read_only")
    client.connect()
    with pytest.raises(PermissionDeniedV37):
        client.send_stimulation_pattern({"abstract_pattern_id": "x"})


def test_v37_metadata_only_disallows_trace_read():
    client = make_external_api_client_v37("axion_maestro", "metadata_only")
    client.connect()
    with pytest.raises(PermissionDeniedV37):
        client.read_spike_events(duration_s=0.1)


def test_v37_commercial_tiers_include_enterprise_and_closed_loop():
    tiers = commercial_tiers_v37()
    names = [t.tier for t in tiers]
    assert any("Enterprise Read-Only" in n for n in names)
    assert any("Closed-Loop" in n for n in names)


def test_v37_report_generation(tmp_path):
    summary = generate_report_v37(tmp_path)
    assert summary["version"] == "v3.7"
    assert summary["platform_count"] == 4
    assert summary["write_denial_passed"] is True
    assert (tmp_path / "BIOGPU_V37_EXTERNAL_API_BIOSDK_REPORT.md").exists()
    assert (tmp_path / "biogpu_v37_external_api_biosdk_bundle.zip").exists()
