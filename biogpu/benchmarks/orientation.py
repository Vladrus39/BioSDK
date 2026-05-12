from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import yaml
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from biogpu.datasets.orientation import generate_orientation_dataset, ORIENTATIONS
from biogpu.benchmarks.pipeline import run_single_frame_pipeline
from biogpu.decoding import LinearReadout
from biogpu.decoding.evaluation import evaluate_predictions
from biogpu.benchmarks.baselines import raw_linear_baseline, raw_mlp_baseline, shuffled_reservoir_score, random_feature_baseline
from biogpu.data import ExperimentLogger, estimate_energy_proxy, reservoir_memory_report
from biogpu.data.reports import orientation_report_markdown, write_html_report
from biogpu.data.hdf5_store import save_arrays_hdf5
from biogpu.data.plots import plot_spike_raster, plot_activity_map


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def plot_confusion(cm, out_path: Path):
    fig = plt.figure(figsize=(5, 4))
    plt.imshow(cm)
    plt.title('Confusion matrix')
    plt.xlabel('Predicted'); plt.ylabel('True')
    plt.xticks(range(len(ORIENTATIONS)), [str(o) for o in ORIENTATIONS])
    plt.yticks(range(len(ORIENTATIONS)), [str(o) for o in ORIENTATIONS])
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha='center', va='center')
    plt.tight_layout(); fig.savefig(out_path, dpi=160); plt.close(fig)


def main(config_path: str = 'configs/orientation.yaml') -> dict:
    cfg = load_config(config_path)
    logger = ExperimentLogger(root=cfg.get('outputs', {}).get('root', 'outputs'))
    ts = logger.timestamp()
    patterns = generate_orientation_dataset(size=cfg.get('image_size', 16), samples_per_class=cfg.get('num_samples_per_class', 80), noise_levels=cfg.get('noise_levels', [0.0, 0.1, 0.2, 0.3]), seed=cfg.get('seed', 42))
    X, y, X_raw, spike_counts, active_ratios, event_counts, artifacts = run_single_frame_pipeline(patterns, cfg, return_artifacts=True)
    indices = np.arange(len(y))
    train_idx, test_idx = train_test_split(indices, train_size=cfg.get('train_fraction', 0.7), random_state=cfg.get('seed', 42), stratify=y)
    readout = LinearReadout(random_state=cfg.get('seed', 42)); readout.fit(X[train_idx], y[train_idx])
    y_pred = readout.predict(X[test_idx]); metrics = evaluate_predictions(y[test_idx], y_pred)
    baselines = {
        'raw_linear': raw_linear_baseline(X_raw[train_idx], y[train_idx], X_raw[test_idx], y[test_idx], seed=cfg.get('seed', 42)),
        'raw_mlp': raw_mlp_baseline(X_raw[train_idx], y[train_idx], X_raw[test_idx], y[test_idx], seed=cfg.get('seed', 42)),
        'random_features': random_feature_baseline(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=cfg.get('seed', 42)),
        'shuffled_reservoir': shuffled_reservoir_score(LinearReadout, X[train_idx], y[train_idx], X[test_idx], y[test_idx], seed=cfg.get('seed', 42)),
    }
    energy_proxy = estimate_energy_proxy(event_counts, spike_counts, active_ratios, readout_features=X.shape[1])
    memory_report = reservoir_memory_report(X, y)
    results = {'benchmark': 'orientation', 'timestamp': ts, 'config_path': config_path, 'metrics': metrics, 'baselines': baselines, 'energy_proxy': energy_proxy, 'memory_report': memory_report, 'interpretation': 'End-to-end BioGPU software pipeline. This is a simulated reservoir result, not proof of biological advantage.'}
    logger.save_json(f'orientation_{ts}', results)
    logger.save_markdown_report(f'orientation_{ts}', orientation_report_markdown(results))
    fig_path = logger.figure_dir / f'confusion_matrix_{ts}.png'; plot_confusion(np.asarray(metrics['confusion_matrix']), fig_path)
    figure_paths = [str(fig_path)]
    sample_spikes = artifacts.get('sample_spikes')
    if sample_spikes is not None:
        raster_path = logger.figure_dir / f'spike_raster_{ts}.png'
        plot_spike_raster(sample_spikes.unit_ids, sample_spikes.spike_times, raster_path, title='Sample simulated spike raster')
        figure_paths.append(str(raster_path))
    sample_counts = artifacts.get('sample_counts')
    if sample_counts is not None:
        activity_path = logger.figure_dir / f'activity_map_{ts}.png'
        plot_activity_map(sample_counts, activity_path, title='Sample activity map')
        figure_paths.append(str(activity_path))
    results['figures'] = {'confusion_matrix': str(fig_path), 'spike_raster': figure_paths[1] if len(figure_paths) > 1 else None, 'activity_map': figure_paths[2] if len(figure_paths) > 2 else None}
    html_path = logger.report_dir / f'orientation_{ts}.html'
    write_html_report(html_path, results, [str(Path(p).relative_to(logger.report_dir.parent)) for p in figure_paths])
    h5_path = logger.exp_dir / f'orientation_arrays_{ts}.h5'; save_arrays_hdf5(str(h5_path), X=X, y=y, X_raw=X_raw, spike_counts=spike_counts, active_ratios=active_ratios, event_counts=event_counts)
    print(json.dumps({'report': str(logger.report_dir / f'orientation_{ts}.md'), 'json': str(logger.exp_dir / f'orientation_{ts}.json'), 'figure': str(fig_path), 'html': str(html_path), 'hdf5': str(h5_path), 'accuracy': metrics['accuracy'], 'baselines': baselines}, ensure_ascii=False, indent=2))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default='configs/orientation.yaml'); args = parser.parse_args(); main(args.config)
