from __future__ import annotations

import argparse
import json
import time

import numpy as np
import yaml
from sklearn.model_selection import train_test_split

from biogpu.benchmarks.baselines import raw_linear_baseline, shuffled_reservoir_score
from biogpu.benchmarks.pipeline import run_sequence_pipeline
from biogpu.data import ExperimentLogger, estimate_energy_proxy, reservoir_memory_report
from biogpu.data.energy_accounting import estimate_system_energy
from biogpu.data.plots import plot_metric_bars
from biogpu.data.reports import benchmark_report_markdown, write_html_report
from biogpu.data.versioning import make_run_metadata
from biogpu.datasets.streaming import generate_streaming_change_dataset
from biogpu.decoding import LinearReadout
from biogpu.decoding.evaluation import evaluate_predictions


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _last_frame_raw(patterns):
    return np.asarray([p.data[-1].reshape(-1) for p in patterns])


def _first_frame_raw(patterns):
    return np.asarray([p.data[0].reshape(-1) for p in patterns])


def _delta_raw(patterns):
    return np.asarray([(p.data[-1] - p.data[0]).reshape(-1) for p in patterns])


def main(config_path: str = "configs/streaming.yaml") -> dict:
    t0 = time.perf_counter()
    cfg = load_config(config_path)
    logger = ExperimentLogger(root=cfg.get("outputs", {}).get("root", "outputs"))
    ts = logger.timestamp()
    patterns = generate_streaming_change_dataset(
        size=cfg.get("image_size", 12),
        samples_per_class=cfg.get("num_samples_per_class", 90),
        sequence_length=cfg.get("sequence_length", 6),
        noise=cfg.get("noise", 0.10),
        seed=cfg.get("seed", 515),
    )
    X, y, X_raw, spike_counts, active_ratios, event_counts = run_sequence_pipeline(patterns, cfg)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(
        idx, train_size=cfg.get("train_fraction", 0.7), random_state=cfg.get("seed", 515), stratify=y
    )
    model = LinearReadout(random_state=cfg.get("seed", 515))
    model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx])
    metrics = evaluate_predictions(y[test_idx], pred)

    last_raw = _last_frame_raw(patterns)
    first_raw = _first_frame_raw(patterns)
    delta_raw = _delta_raw(patterns)
    baselines = {
        "first_frame_only_raw_linear": raw_linear_baseline(first_raw[train_idx], y[train_idx], first_raw[test_idx], y[test_idx], seed=cfg.get("seed", 515)),
        "last_frame_only_raw_linear": raw_linear_baseline(last_raw[train_idx], y[train_idx], last_raw[test_idx], y[test_idx], seed=cfg.get("seed", 515)),
        "delta_frame_raw_linear": raw_linear_baseline(delta_raw[train_idx], y[train_idx], delta_raw[test_idx], y[test_idx], seed=cfg.get("seed", 515)),
        "full_sequence_raw_linear_upper_bound": raw_linear_baseline(X_raw[train_idx], y[train_idx], X_raw[test_idx], y[test_idx], seed=cfg.get("seed", 515)),
        "shuffled_reservoir": shuffled_reservoir_score(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=cfg.get("seed", 515)),
    }
    energy_proxy = estimate_energy_proxy(event_counts, spike_counts, active_ratios, readout_features=X.shape[1])
    elapsed = time.perf_counter() - t0
    energy_accounting = estimate_system_energy(
        energy_proxy,
        task_count=len(patterns),
        seconds=elapsed,
        host_watts=float(cfg.get("energy", {}).get("host_watts", 15.0)),
        mode="simulation_proxy",
    )
    comparison = {"biogpu_reservoir": metrics["accuracy"]} | baselines
    fig_path = logger.figure_dir / f"streaming_comparison_{ts}.png"
    plot_metric_bars(comparison, fig_path, title="Streaming change benchmark")
    results = {
        **make_run_metadata("streaming_change", cfg, version="0.5"),
        "timestamp": ts,
        "config_path": config_path,
        "metrics": metrics,
        "baselines": baselines,
        "energy_proxy": energy_proxy,
        "energy_accounting": energy_accounting,
        "memory_report": reservoir_memory_report(X, y),
        "figures": {"comparison": str(fig_path)},
        "interpretation": "Online/streaming task: tests whether reservoir state helps detect changes across a stream. Delta/full-sequence raw baselines are upper bounds, not online-memory equivalents.",
    }
    logger.save_json(f"streaming_{ts}", results)
    logger.save_markdown_report(f"streaming_{ts}", benchmark_report_markdown(results))
    html_path = logger.report_dir / f"streaming_{ts}.html"
    write_html_report(html_path, results, [str(fig_path.relative_to(logger.report_dir.parent))])
    print(json.dumps({"report": str(logger.report_dir / f"streaming_{ts}.md"), "html": str(html_path), "json": str(logger.exp_dir / f"streaming_{ts}.json"), "accuracy": metrics["accuracy"], "baselines": baselines}, ensure_ascii=False, indent=2))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/streaming.yaml")
    args = parser.parse_args()
    main(args.config)
