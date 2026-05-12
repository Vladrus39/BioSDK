from __future__ import annotations

import pytest

from biogpu.enterprise.licensing_v39 import (
    BioSDKDeploymentModeV39,
    build_commercial_package_v39,
    default_enterprise_license_tiers_v39,
)
from biogpu.safety.boundary_v35 import SafetyViolationV35, assert_no_forbidden_payload_v35


def test_v39_commercial_package_validates_without_errors():
    package = build_commercial_package_v39()
    assert package.version == "v3.9"
    assert package.validate() == []
    assert len(package.license_tiers) >= 4
    assert "Enterprise Read-Only BioSDK" in [t.display_name for t in package.license_tiers]


def test_v39_first_paid_tier_is_read_only_not_closed_loop():
    tiers = {t.tier_id: t for t in default_enterprise_license_tiers_v39()}
    readonly = tiers["enterprise_readonly"]
    assert BioSDKDeploymentModeV39.ENTERPRISE_READ_ONLY.value in readonly.allowed_deployment_modes
    assert BioSDKDeploymentModeV39.LAB_APPROVED_CLOSED_LOOP.value not in readonly.allowed_deployment_modes
    assert "writes denied" in readonly.compliance_boundary.lower() or "read-only" in readonly.compliance_boundary.lower()


def test_v39_closed_loop_addon_is_future_lab_gated():
    tiers = {t.tier_id: t for t in default_enterprise_license_tiers_v39()}
    closed = tiers["lab_approved_closed_loop_addon"]
    assert closed.allowed_deployment_modes == (BioSDKDeploymentModeV39.LAB_APPROVED_CLOSED_LOOP.value,)
    assert "future" in closed.compliance_boundary.lower()
    assert "sop" in closed.compliance_boundary.lower()


def test_v39_safety_boundary_rejects_unsafe_commercial_payload():
    with pytest.raises(SafetyViolationV35):
        assert_no_forbidden_payload_v35({"enterprise_config": {"pulse_width": 1}}, context="enterprise")
