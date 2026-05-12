from __future__ import annotations
from typing import Any
from biogpu.closed_loop.base_v28 import ClosedLoopObservationV28, RewardSignalV28

class AccuracyConfidenceRewardV28:
    reward_id = "accuracy_confidence_reward_v28"

    def __init__(self, target_confidence: float = 0.75):
        self.target_confidence = float(target_confidence)

    def score(self, obs: ClosedLoopObservationV28) -> RewardSignalV28:
        obs.validate()
        conf = 0.0 if obs.confidence is None else float(obs.confidence)
        correct = (obs.expected is not None and obs.prediction == obs.expected)
        conf_gap = max(0.0, self.target_confidence - conf)
        reward = (1.0 if correct else 0.0) + 0.25 * conf
        error = (0.0 if correct else 1.0) + conf_gap
        success = bool(correct and conf >= self.target_confidence)
        reason = "correct_and_confident" if success else ("correct_low_confidence" if correct else "incorrect_or_unknown")
        return RewardSignalV28(reward=reward, error=error, success=success, reason=reason, metadata={"confidence": conf, "correct": correct})
