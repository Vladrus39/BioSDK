from __future__ import annotations
import argparse, json
import numpy as np
import yaml
from sklearn.model_selection import train_test_split
from biogpu.datasets.delayed_match import generate_delayed_match_dataset
from biogpu.benchmarks.pipeline import run_sequence_pipeline
from biogpu.decoding import LinearReadout
from biogpu.decoding.evaluation import evaluate_predictions
from biogpu.benchmarks.baselines import raw_linear_baseline, shuffled_reservoir_score
from biogpu.data import ExperimentLogger, estimate_energy_proxy, reservoir_memory_report
from biogpu.data.reports import benchmark_report_markdown, write_html_report
from biogpu.data.plots import plot_metric_bars


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _last_frame_raw(patterns):
    return np.asarray([p.data[-1].reshape(-1) for p in patterns])


def _bag_of_frames_raw(patterns):
    # Orderless baseline: sum/mean over frames; it loses temporal order.
    return np.asarray([p.data.mean(axis=0).reshape(-1) for p in patterns])


def main(config_path: str = 'configs/delayed_match.yaml') -> dict:
    cfg = load_config(config_path)
    logger = ExperimentLogger(root=cfg.get('outputs', {}).get('root', 'outputs'))
    ts = logger.timestamp()
    patterns = generate_delayed_match_dataset(
        size=cfg.get('image_size', 12),
        samples_per_class=cfg.get('num_samples_per_class', 80),
        delay_frames=cfg.get('delay_frames', 2),
        noise=cfg.get('noise', 0.12),
        seed=cfg.get('seed', 123),
    )
    X, y, X_raw, spike_counts, active_ratios, event_counts = run_sequence_pipeline(patterns, cfg)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, train_size=cfg.get('train_fraction', 0.7), random_state=cfg.get('seed', 123), stratify=y)
    model = LinearReadout(random_state=cfg.get('seed', 123))
    model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx])
    metrics = evaluate_predictions(y[test_idx], pred)
    last_raw = _last_frame_raw(patterns)
    bag_raw = _bag_of_frames_raw(patterns)
    baselines = {
        'last_frame_only_raw_linear': raw_linear_baseline(last_raw[train_idx], y[train_idx], last_raw[test_idx], y[test_idx], seed=cfg.get('seed', 123)),
        'orderless_bag_of_frames_raw_linear': raw_linear_baseline(bag_raw[train_idx], y[train_idx], bag_raw[test_idx], y[test_idx], seed=cfg.get('seed', 123)),
        'full_sequence_raw_linear_upper_bound': raw_linear_baseline(X_raw[train_idx], y[train_idx], X_raw[test_idx], y[test_idx], seed=cfg.get('seed', 123)),
        'shuffled_reservoir': shuffled_reservoir_score(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=cfg.get('seed', 123)),
    }
    energy_proxy = estimate_energy_proxy(event_counts, spike_counts, active_ratios, readout_features=X.shape[1])
    comparison = {'biogpu_reservoir': metrics['accuracy']} | baselines
    fig_path = logger.figure_dir / f'delayed_match_comparison_{ts}.png'
    plot_metric_bars(comparison, fig_path, title='Delayed match benchmark')
    results = {
        'benchmark': 'delayed_match_memory',
        'timestamp': ts,
        'metrics': metrics,
        'baselines': baselines,
        'energy_proxy': energy_proxy,
        'memory_report': reservoir_memory_report(X, y),
        'figures': {'comparison': str(fig_path)},
        'interpretation': 'Delayed match tests whether the reservoir state carries cue information across delay frames. Last-frame and orderless baselines are intentionally weak; full-sequence raw is an upper bound, not a fair online-memory baseline.'
    }
    logger.save_json(f'delayed_match_{ts}', results)
    logger.save_markdown_report(f'delayed_match_{ts}', benchmark_report_markdown(results))
    html_path = logger.report_dir / f'delayed_match_{ts}.html'
    write_html_report(html_path, results, [str(fig_path.relative_to(logger.report_dir.parent))])
    print(json.dumps({'report': str(logger.report_dir / f'delayed_match_{ts}.md'), 'html': str(html_path), 'json': str(logger.exp_dir / f'delayed_match_{ts}.json'), 'accuracy': metrics['accuracy'], 'baselines': baselines}, ensure_ascii=False, indent=2))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default='configs/delayed_match.yaml'); args = parser.parse_args(); main(args.config)
