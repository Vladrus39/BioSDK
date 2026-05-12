from biogpu.closed_loop.base_v28 import ClosedLoopConfigV28, ClosedLoopDecisionV28
from biogpu.closed_loop.controller_v28 import BioGPUClosedLoopControllerV28
from biogpu.closed_loop.registry_v28 import closed_loop_registry_summary_v28


def test_closed_loop_config_rejects_unsafe_metadata():
    cfg = ClosedLoopConfigV28(loop_id="x", benchmark_id="B4", metadata={"voltage": 1})
    try:
        cfg.validate()
    except ValueError as e:
        assert "Unsafe" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_decision_rejects_unsafe_payload():
    d = ClosedLoopDecisionV28("continue", {"pulse_width": 1})
    try:
        d.validate()
    except ValueError as e:
        assert "Unsafe" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_closed_loop_controller_runs_dry_run():
    cfg = ClosedLoopConfigV28(loop_id="test_loop", benchmark_id="B4_adaptive_closed_loop", max_steps=4, target_confidence=0.2)
    out = BioGPUClosedLoopControllerV28(cfg).run({"spatial": [0,1,2,1], "temporal": [1,0,1,0]}, expected="target")
    assert out.status == "completed"
    assert len(out.steps) >= 1
    assert out.live_output_performed is False
    assert out.steps[0].observation.features


def test_registry_summary_has_modes():
    s = closed_loop_registry_summary_v28()
    assert "dry_run" in s["mode_support"]
    assert "live_lab_requires_vendor_sop" in s["mode_support"]
