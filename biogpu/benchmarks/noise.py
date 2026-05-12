from __future__ import annotations
import argparse, json
import numpy as np
import yaml
from sklearn.model_selection import train_test_split
from biogpu.datasets.noise import generate_noise_robustness_dataset
from biogpu.benchmarks.pipeline import run_single_frame_pipeline
from biogpu.decoding import LinearReadout
from biogpu.decoding.evaluation import evaluate_predictions
from biogpu.benchmarks.baselines import raw_linear_baseline, shuffled_reservoir_score
from biogpu.data import ExperimentLogger, estimate_energy_proxy
from biogpu.data.reports import benchmark_report_markdown


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f: return yaml.safe_load(f)


def main(config_path: str = 'configs/noise.yaml') -> dict:
    cfg = load_config(config_path)
    logger = ExperimentLogger(root=cfg.get('outputs', {}).get('root', 'outputs'))
    ts = logger.timestamp()
    patterns = generate_noise_robustness_dataset(size=cfg.get('image_size', 16), samples_per_class=cfg.get('num_samples_per_class', 40), noise_levels=cfg.get('noise_levels', [0.0, 0.15, 0.3, 0.45, 0.6]), seed=cfg.get('seed', 43))
    X, y, X_raw, spike_counts, active_ratios, event_counts = run_single_frame_pipeline(patterns, cfg)
    noise_levels = np.asarray([float(p.metadata['noise_level']) for p in patterns])
    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(idx, train_size=cfg.get('train_fraction', 0.7), random_state=cfg.get('seed', 43), stratify=y)
    model = LinearReadout(random_state=cfg.get('seed', 43)); model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx]); metrics = evaluate_predictions(y[test_idx], pred)
    curve = {}
    for nl in sorted(set(noise_levels[test_idx])):
        mask = noise_levels[test_idx] == nl
        if mask.any(): curve[str(float(nl))] = float(np.mean(pred[mask] == y[test_idx][mask]))
    baselines = {
        'raw_linear': raw_linear_baseline(X_raw[train_idx], y[train_idx], X_raw[test_idx], y[test_idx], seed=cfg.get('seed', 43)),
        'shuffled_reservoir': shuffled_reservoir_score(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=cfg.get('seed', 43)),
    }
    results = {'benchmark': 'noise_robustness', 'timestamp': ts, 'metrics': metrics, 'noise_curve': curve, 'baselines': baselines, 'energy_proxy': estimate_energy_proxy(event_counts, spike_counts, active_ratios, readout_features=X.shape[1]), 'interpretation': 'Noise benchmark checks whether the reservoir representation remains separable under increasing input noise.'}
    logger.save_json(f'noise_{ts}', results); logger.save_markdown_report(f'noise_{ts}', benchmark_report_markdown(results))
    print(json.dumps({'report': str(logger.report_dir / f'noise_{ts}.md'), 'json': str(logger.exp_dir / f'noise_{ts}.json'), 'accuracy': metrics['accuracy'], 'noise_curve': curve}, ensure_ascii=False, indent=2))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default='configs/noise.yaml'); args = parser.parse_args(); main(args.config)
