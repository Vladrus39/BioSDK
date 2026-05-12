from __future__ import annotations
from typing import Any, Dict
from biogpu.closed_loop.base_v28 import ClosedLoopConfigV28, ClosedLoopDecisionV28, ClosedLoopObservationV28, RewardSignalV28

class ConfidenceSeekingPolicyV28:
    policy_id = "confidence_seeking_policy_v28"

    def decide(self, config: ClosedLoopConfigV28, obs: ClosedLoopObservationV28, reward: RewardSignalV28, current_payload: Dict[str, Any]) -> ClosedLoopDecisionV28:
        config.validate(); obs.validate(); reward.validate()
        if reward.success:
            return ClosedLoopDecisionV28("stop_success", dict(current_payload), {"policy_id": self.policy_id}, "success gate reached")
        conf = 0.0 if obs.confidence is None else float(obs.confidence)
        next_payload = dict(current_payload)
        step = int(obs.step_index) + 1
        next_payload["step"] = step
        # safe abstract adaptation only, no live stimulation values
        gain = float(next_payload.get("abstract_gain", 1.0))
        exploration = float(next_payload.get("abstract_exploration", config.exploration_floor))
        if conf < config.target_confidence:
            next_payload["abstract_gain"] = min(1.0, gain + 0.10)
            next_payload["abstract_exploration"] = min(1.0, exploration + 0.05)
            return ClosedLoopDecisionV28("increase_exploration", next_payload, {"policy_id": self.policy_id, "confidence": conf}, "confidence below target")
        next_payload["abstract_exploration"] = max(config.exploration_floor, exploration * 0.9)
        return ClosedLoopDecisionV28("continue", next_payload, {"policy_id": self.policy_id, "confidence": conf}, "continue with reduced exploration")
