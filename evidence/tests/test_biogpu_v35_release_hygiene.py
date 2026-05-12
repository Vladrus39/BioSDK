from pathlib import Path
import tempfile

import pytest

from biogpu.readout.base_v27 import ReadoutFeatureBatch
from biogpu.readout.registry_v27 import build_readout_registry_v27
from biogpu.safety.boundary_v35 import (
    SafetyViolationV35,
    assert_no_forbidden_keys_v35,
    assert_no_forbidden_payload_v35,
    safety_boundary_summary_v35,
)
from biogpu.safety.governance_v35 import evaluate_mode_v35
from biogpu.release.release_hygiene_v35 import build_release_manifest_v35, write_release_hygiene_outputs_v35


def _toy_batch():
    return ReadoutFeatureBatch(
        ["f0", "f1"],
        [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9], [1.1, -0.1], [-0.1, 1.1]],
        ["A", "A", "B", "B", "A", "B"],
    )


def test_logistic_and_svm_are_real_sklearn_models():
    reg = build_readout_registry_v27()
    for rid in ("logistic_l2_v27", "linear_svm_v27"):
        model = reg[rid].fit(_toy_batch())
        pred = model.predict_one([1.0, 0.0])
        assert pred.prediction == "A"
        assert pred.metadata["real_sklearn_model"] is True
        assert pred.confidence is None or 0.0 <= pred.confidence <= 1.0


def test_unified_safety_boundary_rejects_forbidden_keys():
    assert_no_forbidden_keys_v35(["abstract_gain", "source"], context="test")
    with pytest.raises(SafetyViolationV35):
        assert_no_forbidden_keys_v35(["voltage"], context="test")
    with pytest.raises(SafetyViolationV35):
        assert_no_forbidden_payload_v35({"nested": {"pulse_width": 1}}, context="test")


def test_governance_allows_read_only_and_blocks_live_mode():
    ok = evaluate_mode_v35("read_only_api", {"source": "metadata"})
    blocked = evaluate_mode_v35("live_lab", {"source": "metadata"})
    assert ok.allowed is True
    assert blocked.allowed is False


def test_release_manifest_checks_current_tree():
    manifest = build_release_manifest_v35(Path("."))
    checks = {c.check_id: c.status for c in manifest.checks}
    assert checks["pkg_version"] == "ok"
    assert checks["docker_entrypoint"] == "ok"
    assert checks["real_sklearn_readouts"] == "ok"
    assert safety_boundary_summary_v35().forbidden_field_count >= 20


def test_release_hygiene_output_generator(tmp_path):
    summary = write_release_hygiene_outputs_v35(tmp_path, Path("."))
    assert summary["checks_ok"] is True
    assert summary["real_sklearn_readouts"] is True
    assert (tmp_path / "BIOGPU_V35_RELEASE_HYGIENE_REPORT.md").exists()
    assert (tmp_path / "biogpu_v35_release_hygiene_bundle.zip").exists()
