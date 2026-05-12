from __future__ import annotations

import pytest

from biogpu.llm.tool_interface_v38 import (
    BioLLMModeV38,
    BioLLMTaskV38,
    BioLLMToolInterfaceV38,
    default_biollm_commercial_tiers_v38,
)
from biogpu.safety.boundary_v35 import SafetyViolationV35


def test_v38_build_manifest_and_run_read_only_tool():
    tool = BioLLMToolInterfaceV38()
    task = BioLLMTaskV38(
        task_id="t1",
        user_goal="detect activity from read-only mock trace",
        mode=BioLLMModeV38.API_READ_ONLY.value,
        platform="mcs_mea2100",
        decoder_id="centroid_v27",
    )
    manifest = tool.build_manifest(task)
    assert manifest.selected_platform == "mcs_mea2100"
    assert manifest.safety["writes_allowed"] is False
    result = tool.run(task)
    assert result.status == "ok"
    assert result.safety["live_output_performed"] is False
    assert result.trace_summary["trace_available"] is True
    assert result.structured_result["biogpu_signal"] in {"low_activity", "activity_detected"}


def test_v38_metadata_only_does_not_read_trace():
    tool = BioLLMToolInterfaceV38()
    task = BioLLMTaskV38(
        task_id="metadata",
        user_goal="confirm platform visibility only",
        mode=BioLLMModeV38.METADATA_ONLY.value,
        platform="finalspark",
    )
    result = tool.run(task)
    assert result.trace_summary["trace_available"] is False
    assert result.readout_prediction is None
    assert result.structured_result["biogpu_signal"] == "metadata_only_no_trace"


def test_v38_rejects_forbidden_live_control_payload():
    task = BioLLMTaskV38(
        task_id="bad",
        user_goal="bad request",
        mode=BioLLMModeV38.API_READ_ONLY.value,
        platform="mcs",
        input_payload={"amplitude": 10, "pulse_width": 1},
    )
    with pytest.raises(SafetyViolationV35):
        task.validate()


def test_v38_commercial_tiers_include_enterprise_and_no_closed_loop_modes():
    tiers = default_biollm_commercial_tiers_v38()
    names = [t.tier for t in tiers]
    assert "Enterprise Read-Only BioSDK" in names
    assert "Enterprise Live Shadow BioSDK" in names
    closed = [t for t in tiers if t.tier == "Lab-Approved Closed Loop Add-on"][0]
    assert closed.allowed_modes == ()
