from __future__ import annotations
from biogpu.closed_loop.controller_v28 import BioGPUClosedLoopControllerV28, DryRunClosedLoopSubstrateV28
from biogpu.closed_loop.policy_v28 import ConfidenceSeekingPolicyV28
from biogpu.closed_loop.reward_v28 import AccuracyConfidenceRewardV28


def closed_loop_registry_summary_v28() -> dict:
    return {
        "controller": BioGPUClosedLoopControllerV28.__name__,
        "substrate": DryRunClosedLoopSubstrateV28.__name__,
        "policy": ConfidenceSeekingPolicyV28.__name__,
        "reward": AccuracyConfidenceRewardV28.__name__,
        "mode_support": ["dry_run", "replay", "power_pc", "live_lab_requires_vendor_sop"],
    }
