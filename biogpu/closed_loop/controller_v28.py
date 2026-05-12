from __future__ import annotations
import hashlib
from typing import Any, Dict, Iterable, List
from biogpu.closed_loop.base_v28 import ClosedLoopConfigV28, ClosedLoopObservationV28, ClosedLoopRunSummaryV28, ClosedLoopStepRecordV28, ClosedLoopDecisionV28, RewardSignalV28
from biogpu.closed_loop.policy_v28 import ConfidenceSeekingPolicyV28
from biogpu.closed_loop.reward_v28 import AccuracyConfidenceRewardV28
from biogpu.encoding.base_v26 import EncoderInput
from biogpu.encoding.registry_v26 import build_encoder_registry_v26
from biogpu.readout.base_v27 import ReadoutFeatureBatch
from biogpu.readout.registry_v27 import build_readout_registry_v27

class DryRunClosedLoopSubstrateV28:
    """Deterministic dry-run substrate for controller tests.

    It maps an abstract pattern to a small feature vector. This is not a live
    device and not a biological claim; it only tests closed-loop mechanics.
    """
    substrate_id = "dry_run_closed_loop_substrate_v28"

    def observe(self, pattern: Dict[str, Any], step_index: int) -> tuple[list[float], list[str]]:
        weights = [float(w) for w in pattern.get("weights", [])]
        n_groups = float(len(pattern.get("target_groups", [])))
        mean_w = sum(weights) / (len(weights) or 1)
        max_w = max(weights) if weights else 0.0
        step_signal = min(1.0, step_index / 10.0)
        # feature vector intentionally simple and deterministic
        return [mean_w, max_w, n_groups / 10.0, step_signal], ["mean_weight", "max_weight", "group_fraction", "step_signal"]

class BioGPUClosedLoopControllerV28:
    def __init__(self, config: ClosedLoopConfigV28, substrate: DryRunClosedLoopSubstrateV28 | None = None):
        config.validate()
        self.config = config
        self.substrate = substrate or DryRunClosedLoopSubstrateV28()
        self.encoders = build_encoder_registry_v26()
        self.readouts = build_readout_registry_v27()
        self.policy = ConfidenceSeekingPolicyV28()
        self.rewarder = AccuracyConfidenceRewardV28(target_confidence=config.target_confidence)

    def _bootstrap_readout(self, feature_names: list[str], expected: Any) -> object:
        readout = self.readouts[self.config.readout_id]
        # two separable labels to make prediction meaningful in dry-run
        batch = ReadoutFeatureBatch(
            feature_names=feature_names,
            X=[[0.15, 0.25, 0.20, 0.0], [0.85, 1.0, 0.80, 0.5]],
            y=["control", expected],
            metadata={"bootstrap": "v2.8 dry-run controller"},
        )
        readout.fit(batch)
        return readout

    def run(self, initial_payload: Dict[str, Any], expected: Any = "target") -> ClosedLoopRunSummaryV28:
        payload = dict(initial_payload)
        steps: list[ClosedLoopStepRecordV28] = []
        encoder = self.encoders[self.config.encoder_id]
        readout = None
        status = "running"
        final_reward = 0.0
        final_success = False
        for step_idx in range(self.config.max_steps):
            item = EncoderInput(task_id=self.config.benchmark_id, payload=payload, metadata={"loop_id": self.config.loop_id})
            pattern = encoder.encode(item)
            pattern_dict = pattern.to_dict()
            features, feature_names = self.substrate.observe(pattern_dict, step_idx)
            if readout is None:
                readout = self._bootstrap_readout(feature_names, expected)
            pred = readout.predict_one(features, feature_names)
            obs = ClosedLoopObservationV28(
                step_index=step_idx,
                pattern_id=pattern.pattern_id,
                features=features,
                feature_names=feature_names,
                prediction=pred.prediction,
                confidence=pred.confidence,
                expected=expected,
                metadata={"decoder_id": pred.decoder_id, "scores": pred.scores},
            )
            reward = self.rewarder.score(obs)
            decision = self.policy.decide(self.config, obs, reward, payload)
            steps.append(ClosedLoopStepRecordV28(step_idx, self.config.encoder_id, self.config.readout_id, pattern_dict, obs, reward, decision))
            final_reward = reward.reward
            final_success = reward.success
            if decision.action in {"stop_success"}:
                status = "completed"
                break
            payload = dict(decision.next_payload)
        else:
            status = "completed"
            # mark max steps decision for last record if not already success
            if steps and not steps[-1].reward.success:
                last = steps[-1]
                max_decision = ClosedLoopDecisionV28("stop_max_steps", last.decision.next_payload, last.decision.policy_state, "max steps reached")
                steps[-1] = ClosedLoopStepRecordV28(last.step_index, last.encoder_id, last.readout_id, last.pattern, last.observation, last.reward, max_decision)
        return ClosedLoopRunSummaryV28(self.config, status, steps, final_reward, final_success, live_output_performed=False)
