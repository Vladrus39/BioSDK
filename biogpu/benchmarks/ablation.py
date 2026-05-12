from __future__ import annotations
import argparse, copy, json
import numpy as np
import yaml
from sklearn.model_selection import train_test_split
from biogpu.datasets.orientation import generate_orientation_dataset
from biogpu.benchmarks.pipeline import run_single_frame_pipeline
from biogpu.decoding import LinearReadout
from biogpu.decoding.evaluation import evaluate_predictions
from biogpu.benchmarks.baselines import shuffled_reservoir_score
from biogpu.data import ExperimentLogger
from biogpu.data.reports import benchmark_report_markdown, write_html_report
from biogpu.data.plots import plot_metric_bars


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _run_variant(cfg: dict, patterns, seed: int) -> dict:
    X, y, X_raw, spike_counts, active_ratios, event_counts = run_single_frame_pipeline(patterns, cfg)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, train_size=cfg.get('train_fraction', 0.7), random_state=seed, stratify=y)
    model = LinearReadout(random_state=seed)
    model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx])
    metrics = evaluate_predictions(y[test_idx], pred)
    shuffled = shuffled_reservoir_score(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=seed)
    return {'accuracy': float(metrics['accuracy']), 'shuffled': float(shuffled), 'reservoir_gain_over_shuffled': float(metrics['accuracy'] - shuffled), 'mean_spikes': float(np.mean(spike_counts)), 'mean_active_ratio': float(np.mean(active_ratios))}


def main(config_path: str = 'configs/ablation.yaml') -> dict:
    cfg = load_config(config_path)
    logger = ExperimentLogger(root=cfg.get('outputs', {}).get('root', 'outputs'))
    ts = logger.timestamp()
    seed = cfg.get('seed', 202)
    patterns = generate_orientation_dataset(size=cfg.get('image_size', 16), samples_per_class=cfg.get('num_samples_per_class', 35), noise_levels=cfg.get('noise_levels', [0.0, 0.2, 0.35]), seed=seed)
    variants = {}
    base = copy.deepcopy(cfg)
    variants['normal_v1_reservoir'] = base
    no_recur = copy.deepcopy(cfg); no_recur['substrate']['state_decay'] = 0.0; no_recur['substrate']['recurrent_strength'] = 0.0; no_recur['substrate']['trace_strength'] = 0.0
    variants['no_recurrent_memory'] = no_recur
    no_v1 = copy.deepcopy(cfg); no_v1['encoder']['use_orientation_banks'] = False
    variants['no_v1_encoder'] = no_v1
    high_noise = copy.deepcopy(cfg); high_noise['substrate']['noise_level'] = max(0.12, float(high_noise['substrate'].get('noise_level', 0.04)) * 3.0)
    variants['high_reservoir_noise'] = high_noise
    results_by_variant = {name: _run_variant(vcfg, patterns, seed) for name, vcfg in variants.items()}
    bars = {k: v['accuracy'] for k, v in results_by_variant.items()}
    fig_path = logger.figure_dir / f'ablation_accuracy_{ts}.png'
    plot_metric_bars(bars, fig_path, title='Ablation accuracy')
    results = {
        'benchmark': 'reservoir_ablation',
        'timestamp': ts,
        'metrics': {'accuracy': results_by_variant['normal_v1_reservoir']['accuracy']},
        'ablations': results_by_variant,
        'figures': {'accuracy_bars': str(fig_path)},
        'interpretation': 'Ablation tests check whether V1 encoding, recurrence, and noise settings materially change reservoir utility. This helps avoid treating any black-box reservoir output as proof.'
    }
    logger.save_json(f'ablation_{ts}', results)
    logger.save_markdown_report(f'ablation_{ts}', benchmark_report_markdown(results))
    html_path = logger.report_dir / f'ablation_{ts}.html'
    write_html_report(html_path, results, [str(fig_path.relative_to(logger.report_dir.parent))])
    print(json.dumps({'report': str(logger.report_dir / f'ablation_{ts}.md'), 'html': str(html_path), 'json': str(logger.exp_dir / f'ablation_{ts}.json'), 'ablations': results_by_variant}, ensure_ascii=False, indent=2))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default='configs/ablation.yaml'); args = parser.parse_args(); main(args.config)
