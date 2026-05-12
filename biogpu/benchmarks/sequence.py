from __future__ import annotations
import argparse, json
import yaml
import numpy as np
from sklearn.model_selection import train_test_split
from biogpu.datasets.sequences import generate_sequence_dataset
from biogpu.benchmarks.pipeline import run_sequence_pipeline
from biogpu.decoding import LinearReadout
from biogpu.decoding.evaluation import evaluate_predictions
from biogpu.benchmarks.baselines import raw_linear_baseline, shuffled_reservoir_score
from biogpu.data import ExperimentLogger, estimate_energy_proxy, reservoir_memory_report
from biogpu.data.reports import benchmark_report_markdown


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f: return yaml.safe_load(f)


def main(config_path: str = 'configs/sequence.yaml') -> dict:
    cfg = load_config(config_path)
    logger = ExperimentLogger(root=cfg.get('outputs', {}).get('root', 'outputs'))
    ts = logger.timestamp()
    patterns = generate_sequence_dataset(size=cfg.get('image_size', 12), samples_per_class=cfg.get('num_samples_per_class', 50), noise=cfg.get('noise', 0.15), seed=cfg.get('seed', 99))
    X, y, X_raw, spike_counts, active_ratios, event_counts = run_sequence_pipeline(patterns, cfg)
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, train_size=cfg.get('train_fraction', 0.7), random_state=cfg.get('seed', 99), stratify=y)
    model = LinearReadout(random_state=cfg.get('seed', 99)); model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx]); metrics = evaluate_predictions(y[test_idx], pred)
    baselines = {
        'raw_linear_full_sequence': raw_linear_baseline(X_raw[train_idx], y[train_idx], X_raw[test_idx], y[test_idx], seed=cfg.get('seed', 99)),
        'shuffled_reservoir': shuffled_reservoir_score(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=cfg.get('seed', 99)),
    }
    results = {'benchmark': 'sequence_memory', 'timestamp': ts, 'metrics': metrics, 'baselines': baselines, 'energy_proxy': estimate_energy_proxy(event_counts, spike_counts, active_ratios, readout_features=X.shape[1]), 'memory_report': reservoir_memory_report(X, y), 'interpretation': 'Sequence benchmark probes whether reservoir state carries order information across multiple stimulations.'}
    logger.save_json(f'sequence_{ts}', results); logger.save_markdown_report(f'sequence_{ts}', benchmark_report_markdown(results))
    print(json.dumps({'report': str(logger.report_dir / f'sequence_{ts}.md'), 'json': str(logger.exp_dir / f'sequence_{ts}.json'), 'accuracy': metrics['accuracy'], 'baselines': baselines}, ensure_ascii=False, indent=2))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default='configs/sequence.yaml'); args = parser.parse_args(); main(args.config)
