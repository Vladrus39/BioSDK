from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from biogpu.safety.boundary_v35 import assert_no_forbidden_payload_v35, safety_boundary_summary_v35

@dataclass(frozen=True)
class GovernanceDecisionV35:
    version: str
    mode: str
    allowed: bool
    reason: str
    boundary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_mode_v35(mode: str, payload: dict[str, Any] | None = None) -> GovernanceDecisionV35:
    """Allow software/replay/read-only modes; reject unsupervised live modes.

    This is a repository governance helper, not a laboratory approval system.
    """
    m = str(mode).strip().lower()
    payload = payload or {}
    assert_no_forbidden_payload_v35(payload, context=f"governance payload for mode={m}")
    allowed_modes = {"replay", "dry_run", "power_pc", "metadata_only", "read_only_api", "live_shadow_read_only"}
    if m in allowed_modes:
        return GovernanceDecisionV35("v3.5", m, True, "Allowed software/replay/read-only mode.", safety_boundary_summary_v35().to_dict())
    return GovernanceDecisionV35("v3.5", m, False, "Live output requires approved lab/vendor backend and is outside this release.", safety_boundary_summary_v35().to_dict())
