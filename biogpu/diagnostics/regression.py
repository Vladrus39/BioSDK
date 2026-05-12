from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ReservoirDiagnostic:
    benchmark: str
    reservoir_accuracy: float
    shuffled_accuracy: float | None
    random_accuracy: float | None
    best_raw_baseline: float | None
    reservoir_margin_vs_shuffled: float | None
    reservoir_margin_vs_random: float | None
    reservoir_margin_vs_best_raw: float | None
    severity: str
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _best_raw_baseline(baselines: dict[str, Any]) -> float | None:
    vals: list[float] = []
    for name, val in baselines.items():
        if not isinstance(val, (int, float)):
            continue
        key = name.lower()
        if "raw" in key or "linear" in key or "mlp" in key or "upper_bound" in key:
            vals.append(float(val))
    return max(vals) if vals else None


def _get_baseline(baselines: dict[str, Any], keywords: tuple[str, ...]) -> float | None:
    for name, val in baselines.items():
        if not isinstance(val, (int, float)):
            continue
        lower = name.lower()
        if any(k in lower for k in keywords):
            return float(val)
    return None


def diagnose_reservoir_signal(result: dict[str, Any], min_positive_margin: float = 0.03) -> ReservoirDiagnostic:
    """Diagnose whether the reservoir is contributing useful signal.

    This is intentionally conservative. The goal is to prevent the project from
    claiming BioGPU progress when a shuffled/random/raw baseline is doing as well
    or better than the reservoir.
    """
    benchmark = str(result.get("benchmark", "unknown"))
    metrics = result.get("metrics", {}) or {}
    baselines = result.get("baselines", {}) or {}
    reservoir_acc = float(metrics.get("accuracy", result.get("accuracy", 0.0)))
    shuffled = _get_baseline(baselines, ("shuffled",))
    random = _get_baseline(baselines, ("random",))
    best_raw = _best_raw_baseline(baselines)

    margin_shuffled = None if shuffled is None else reservoir_acc - shuffled
    margin_random = None if random is None else reservoir_acc - random
    margin_raw = None if best_raw is None else reservoir_acc - best_raw

    negative_flags = []
    if margin_shuffled is not None and margin_shuffled < min_positive_margin:
        negative_flags.append("not_above_shuffled")
    if margin_random is not None and margin_random < min_positive_margin:
        negative_flags.append("not_above_random")
    if margin_raw is not None and margin_raw < -0.05:
        negative_flags.append("below_raw_baseline")

    if "below_raw_baseline" in negative_flags and ("not_above_shuffled" in negative_flags or "not_above_random" in negative_flags):
        severity = "red"
        recommendation = "Stop performance claims; pivot to real-signal path or redesign task/substrate."
    elif negative_flags:
        severity = "yellow"
        recommendation = "Treat result as weak; run repeated seeds and ablations before making claims."
    else:
        severity = "green"
        recommendation = "Reservoir shows positive signal; validate across seeds and stronger baselines."

    return ReservoirDiagnostic(
        benchmark=benchmark,
        reservoir_accuracy=reservoir_acc,
        shuffled_accuracy=shuffled,
        random_accuracy=random,
        best_raw_baseline=best_raw,
        reservoir_margin_vs_shuffled=margin_shuffled,
        reservoir_margin_vs_random=margin_random,
        reservoir_margin_vs_best_raw=margin_raw,
        severity=severity,
        recommendation=recommendation,
    )
