from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable

import yaml


@dataclass(frozen=True)
class MetricSummary:
    name: str
    count: int
    mean: float
    stdev: float
    minimum: float
    maximum: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def aggregate_metric(values: list[float], name: str = "accuracy") -> MetricSummary:
    if not values:
        raise ValueError("Cannot aggregate empty metric list")
    return MetricSummary(
        name=name,
        count=len(values),
        mean=float(statistics.fmean(values)),
        stdev=float(statistics.stdev(values)) if len(values) > 1 else 0.0,
        minimum=float(min(values)),
        maximum=float(max(values)),
    )


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: str | Path, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def summarize_runs(results: list[dict[str, Any]], metric_key: str = "accuracy") -> dict[str, Any]:
    acc = [float(r.get("metrics", {}).get(metric_key, 0.0)) for r in results]
    summary = aggregate_metric(acc, metric_key).to_dict()
    baseline_values: dict[str, list[float]] = {}
    for r in results:
        for name, value in (r.get("baselines", {}) or {}).items():
            if isinstance(value, (int, float)):
                baseline_values.setdefault(name, []).append(float(value))
    baseline_summary = {k: aggregate_metric(v, k).to_dict() for k, v in baseline_values.items() if v}
    return {"metric": summary, "baselines": baseline_summary, "runs": len(results)}


def run_repeated_seeds(
    benchmark_main: Callable[[str], dict[str, Any]],
    base_config_path: str | Path,
    seeds: list[int],
    output_dir: str | Path = "outputs/repeated_seed_configs",
) -> dict[str, Any]:
    """Run an existing benchmark main(config_path) across seeds.

    This is a simple reproducibility scaffold, not a performance optimizer.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    base_cfg = load_yaml(base_config_path)
    results = []
    for seed in seeds:
        cfg = dict(base_cfg)
        cfg["seed"] = int(seed)
        cfg_path = output / f"{Path(base_config_path).stem}_seed_{seed}.yaml"
        write_yaml(cfg_path, cfg)
        results.append(benchmark_main(str(cfg_path)))
    return summarize_runs(results)
