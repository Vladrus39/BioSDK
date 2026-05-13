"""
BioGPU Runtime v3.0 — Full biological computing pipeline.

Wires together the original BioGPU architecture:
    NSI-1.0 ingest → Encoder → SimulatedMEA reservoir → Readout → Evidence

This is the REAL BioGPU: recurrent reservoir dynamics on real neural data,
not sklearn on static features. The reservoir (SimulatedMEA) is a 256-unit
recurrent network with state decay, trace memory, and optional plasticity.

Architecture:
    NSI window (ch × samples) → RateEncoder → AbstractBioPattern
    → StimPattern → SimulatedMEA.send_stimulation()
    → SimulatedMEA.read_spikes() → SpikeTrain
    → reservoir features (firing rates per unit) → CentroidReadoutV27
    → ReadoutPrediction → EvidenceBundle
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.substrates.simulated_mea import SimulatedMEA
from biogpu.encoding.rate_v26 import RateEncoderV26
from biogpu.encoding.base_v26 import EncoderInput
from biogpu.readout.centroid_v27 import CentroidReadoutV27
from biogpu.readout.base_v27 import ReadoutFeatureBatch, ReadoutPrediction
from biogpu.schemas.types import StimPattern, SpikeTrain
from biogpu.nsi import _default_feature_vector, DEFAULT_FEATURE_NAMES


@dataclass
class ReservoirConfig:
    """Configuration for the SimulatedMEA reservoir."""
    num_electrodes: int = 256
    reservoir_units: int = 256
    connectivity_density: float = 0.06
    noise_level: float = 0.035
    spontaneous_rate: float = 0.008
    state_decay: float = 0.88
    trace_decay: float = 0.96
    gain: float = 1.35
    recurrent_strength: float = 0.85
    input_strength: float = 1.25
    trace_strength: float = 0.35
    plasticity_strength: float = 0.0
    readout_temperature: float = 3.0
    seed: int = 42


@dataclass
class BioGPURunResult:
    """Result of a single BioGPU pipeline run."""
    window_id: int
    nsi_window_shape: tuple
    pattern_id: str
    n_spikes: int
    reservoir_features: np.ndarray
    prediction: Any
    confidence: float | None
    target_label: Any | None
    latency_ms: float


@dataclass
class BioGPUBenchmarkResult:
    """Aggregate benchmark results from BioGPU pipeline."""
    config: dict
    n_windows: int
    n_reservoir_units: int
    n_features_nsi: int
    n_features_reservoir: int
    accuracy: float
    balanced_accuracy: float
    chance_level: float
    per_class_metrics: dict
    run_results: list[BioGPURunResult] = field(default_factory=list)
    sklearn_baseline: dict | None = None


def _window_to_stim_pattern(
    window: np.ndarray,
    pattern_id: str,
    num_electrodes: int = 256,
) -> StimPattern:
    """Convert a neural data window into a stimulation pattern for the reservoir.

    Maps each channel to a set of electrodes. Channel intensity is derived
    from the RMS of that channel's signal, normalized to [-1, 1].
    """
    n_channels = window.shape[0]
    electrodes_per_channel = max(1, num_electrodes // n_channels)

    channels = []
    intensities = []
    times = []

    for ch in range(n_channels):
        seg = window[ch, :].astype(np.float64)
        rms = float(np.sqrt(np.mean(seg**2)))
        # Normalize to reasonable range
        intensity = np.tanh(rms)  # maps [0, inf) → [0, 1)

        for e in range(electrodes_per_channel):
            electrode_id = ch * electrodes_per_channel + e
            if electrode_id >= num_electrodes:
                break
            channels.append(electrode_id)
            intensities.append(float(intensity))
            times.append(0.0)

    return StimPattern(
        substrate_id="simulated_mea_v3",
        channels=channels,
        times=times,
        intensities=intensities,
        safety_class="simulation_only",
        metadata={"pattern_id": pattern_id, "n_channels": n_channels},
    )


def _spike_train_to_firing_rates(
    spike_train: SpikeTrain,
    n_units: int,
    window_ms: float = 20.0,
) -> np.ndarray:
    """Convert a SpikeTrain to firing rate vector (Hz) per reservoir unit."""
    rates = np.zeros(n_units, dtype=np.float32)
    window_s = window_ms / 1000.0

    if spike_train.unit_ids:
        for uid in spike_train.unit_ids:
            if 0 <= uid < n_units:
                rates[uid] += 1.0

        rates = rates / window_s  # Convert to Hz

    return rates


def run_biogpu_pipeline(
    windows: list[np.ndarray],
    labels: np.ndarray | None = None,
    reservoir_config: dict | None = None,
    num_electrodes: int = 256,
    readout_window_ms: float = 20.0,
) -> BioGPUBenchmarkResult:
    """Run the full BioGPU pipeline on a set of NSI-1.0 windows.

    Args:
        windows: List of (channels, samples) arrays from NSI-1.0
        labels: Optional ground-truth labels
        reservoir_config: SimulatedMEA configuration overrides
        num_electrodes: Number of virtual electrodes
        readout_window_ms: Spike readout window in ms

    Returns:
        BioGPUBenchmarkResult with accuracy and per-class metrics
    """
    config = dict(reservoir_config or {})
    cfg = ReservoirConfig(**(config if config else {}))
    cfg.num_electrodes = num_electrodes

    # 1. Initialize reservoir
    reservoir = SimulatedMEA(seed=cfg.seed)
    reservoir.configure({
        "num_electrodes": num_electrodes,
        "reservoir_units": cfg.reservoir_units,
        "connectivity_density": cfg.connectivity_density,
        "noise_level": cfg.noise_level,
        "spontaneous_rate": cfg.spontaneous_rate,
        "state_decay": cfg.state_decay,
        "trace_decay": cfg.trace_decay,
        "gain": cfg.gain,
        "recurrent_strength": cfg.recurrent_strength,
        "input_strength": cfg.input_strength,
        "trace_strength": cfg.trace_strength,
        "plasticity_strength": cfg.plasticity_strength,
        "readout_temperature": cfg.readout_temperature,
    })
    reservoir.connect()

    # 2. Initialize encoder
    encoder = RateEncoderV26()

    # 3. Process each window through the pipeline
    run_results = []
    all_reservoir_features = []
    all_labels_used = []

    for i, window in enumerate(windows):
        t0 = time.perf_counter()

        # Skip bad windows
        if window.size == 0 or not np.isfinite(window).all():
            continue

        # Reset reservoir state between windows for independent processing
        reservoir.reset_state()

        # Encode: window → stimulation pattern
        pattern_id = f"window_{i:06d}"
        stim = _window_to_stim_pattern(window, pattern_id, num_electrodes)

        # Feed pattern into reservoir
        reservoir.send_stimulation(stim)

        # Read reservoir spike output
        spike_train = reservoir.read_spikes(window_ms=readout_window_ms)

        # Extract reservoir features: firing rates per unit
        res_features = _spike_train_to_firing_rates(
            spike_train, cfg.reservoir_units, readout_window_ms
        )

        latency_ms = (time.perf_counter() - t0) * 1000.0

        all_reservoir_features.append(res_features)

        label = None if labels is None else (
            int(labels[i]) if i < len(labels) else None
        )
        all_labels_used.append(label)

        run_results.append(BioGPURunResult(
            window_id=i,
            nsi_window_shape=window.shape,
            pattern_id=pattern_id,
            n_spikes=len(spike_train.unit_ids),
            reservoir_features=res_features,
            prediction=None,  # Filled after readout training
            confidence=None,
            target_label=label,
            latency_ms=latency_ms,
        ))

    reservoir.close()

    # 4. Train readout on reservoir features
    X_reservoir = np.array(all_reservoir_features, dtype=np.float32)
    n_reservoir_units = cfg.reservoir_units

    # Generate feature names
    feature_names = [f"unit_{u}_rate" for u in range(n_reservoir_units)]

    if labels is not None and len(all_labels_used) > 0:
        # Filter out None labels
        valid_idx = [j for j, l in enumerate(all_labels_used) if l is not None]
        if len(valid_idx) < 2:
            return BioGPUBenchmarkResult(
                config=cfg.__dict__,
                n_windows=len(windows),
                n_reservoir_units=n_reservoir_units,
                n_features_nsi=windows[0].shape[1] if windows else 0,
                n_features_reservoir=n_reservoir_units,
                accuracy=0.0,
                balanced_accuracy=0.0,
                chance_level=0.0,
                per_class_metrics={},
                run_results=run_results,
            )

        X_valid = X_reservoir[valid_idx]
        y_valid = np.array([all_labels_used[j] for j in valid_idx])

        # Split: first 60% train, last 40% test
        n_train = int(len(X_valid) * 0.6)
        if n_train < 1:
            n_train = 1
        if n_train >= len(X_valid):
            n_train = len(X_valid) - 1

        X_train = X_valid[:n_train]
        y_train = y_valid[:n_train]
        X_test = X_valid[n_train:]
        y_test = y_valid[n_train:]

        # Train centroid readout
        readout = CentroidReadoutV27()
        batch = ReadoutFeatureBatch(
            feature_names=feature_names,
            X=X_train.tolist(),
            y=y_train.tolist(),
            metadata={"pipeline": "biogpu_v3"},
        )
        readout.fit(batch)

        # Predict on test set
        correct = 0
        per_class_correct = {}
        per_class_total = {}

        for j, (x, true_label) in enumerate(zip(X_test, y_test)):
            pred = readout.predict_one(x.tolist(), feature_names)
            # Update run results
            for rr in run_results:
                if rr.window_id == valid_idx[n_train + j]:
                    rr.prediction = pred.prediction
                    rr.confidence = pred.confidence
                    break

            true_label_str = str(true_label)
            per_class_total[true_label_str] = per_class_total.get(true_label_str, 0) + 1
            if str(pred.prediction) == true_label_str:
                correct += 1
                per_class_correct[true_label_str] = per_class_correct.get(true_label_str, 0) + 1

        accuracy = correct / len(X_test) if len(X_test) > 0 else 0.0

        # Balanced accuracy
        recalls = []
        for cls in set(y_test):
            cls_str = str(cls)
            total_c = per_class_total.get(cls_str, 0)
            correct_c = per_class_correct.get(cls_str, 0)
            recalls.append(correct_c / total_c if total_c > 0 else 0.0)
        balanced_accuracy = float(np.mean(recalls)) if recalls else 0.0

        n_classes = len(set(y_test))
        chance = 1.0 / n_classes if n_classes > 0 else 0.0

        per_class = {}
        for cls in sorted(set(y_test)):
            cls_str = str(cls)
            per_class[cls_str] = {
                "n_total": per_class_total.get(cls_str, 0),
                "n_correct": per_class_correct.get(cls_str, 0),
                "recall": round(
                    per_class_correct.get(cls_str, 0) / max(1, per_class_total.get(cls_str, 0)),
                    4,
                ),
            }

        return BioGPUBenchmarkResult(
            config=cfg.__dict__,
            n_windows=len(windows),
            n_reservoir_units=n_reservoir_units,
            n_features_nsi=windows[0].shape[1] if windows else 0,
            n_features_reservoir=n_reservoir_units,
            accuracy=round(accuracy, 4),
            balanced_accuracy=round(balanced_accuracy, 4),
            chance_level=round(chance, 4),
            per_class_metrics=per_class,
            run_results=run_results,
        )
    else:
        return BioGPUBenchmarkResult(
            config=cfg.__dict__,
            n_windows=len(windows),
            n_reservoir_units=n_reservoir_units,
            n_features_nsi=windows[0].shape[1] if windows else 0,
            n_features_reservoir=n_reservoir_units,
            accuracy=0.0,
            balanced_accuracy=0.0,
            chance_level=0.0,
            per_class_metrics={},
            run_results=run_results,
        )


def run_biogpu_vs_sklearn(
    windows: list[np.ndarray],
    labels: np.ndarray,
    nsi_features: np.ndarray,
    reservoir_config: dict | None = None,
) -> dict:
    """Run BioGPU pipeline and compare against sklearn baseline.

    Returns dict with both results for honest comparison.
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.ensemble import RandomForestClassifier

    # Filter valid windows
    valid_mask = np.array([
        w.size > 0 and np.isfinite(w).all()
        for w in windows
    ])
    valid_idx = np.where(valid_mask)[0]

    if len(valid_idx) < 4:
        return {"error": "Not enough valid windows"}

    windows_valid = [windows[i] for i in valid_idx]
    labels_valid = labels[valid_idx]

    # BioGPU pipeline
    print("  Running BioGPU reservoir pipeline...")
    t0 = time.time()
    biogpu_result = run_biogpu_pipeline(
        windows_valid,
        labels_valid,
        reservoir_config=reservoir_config,
    )
    biogpu_time_s = time.time() - t0
    print(f"    BioGPU: {biogpu_result.balanced_accuracy:.4f} balanced accuracy "
          f"(chance={biogpu_result.chance_level:.4f}), "
          f"{biogpu_result.n_windows} windows, "
          f"{biogpu_time_s:.1f}s")

    # sklearn baseline on NSI features
    print("  Running sklearn baseline on NSI features...")
    nsi_features_valid = nsi_features[valid_idx]

    # Filter non-finite features
    finite_mask = np.isfinite(nsi_features_valid).all(axis=1)
    X_nsi = nsi_features_valid[finite_mask]
    y_nsi = labels_valid[finite_mask]

    if len(np.unique(y_nsi)) < 2:
        return {
            "biogpu": biogpu_result.__dict__ if hasattr(biogpu_result, '__dict__') else {},
            "sklearn": {"error": "Single class"},
            "biogpu_time_s": biogpu_time_s,
        }

    scaler = StandardScaler()
    X_s = scaler.fit_transform(X_nsi)

    n_classes = len(np.unique(y_nsi))
    chance = 1.0 / n_classes

    sklearn_results = {}
    for clf_name, clf in [
        ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42)),
    ]:
        try:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scores = cross_val_score(clf, X_s, y_nsi, cv=cv, scoring="balanced_accuracy")
            sklearn_results[clf_name] = {
                "balanced_accuracy_cv": round(float(scores.mean()), 4),
                "std": round(float(scores.std()), 4),
                "chance": round(chance, 4),
            }
            print(f"    {clf_name}: {scores.mean():.4f} +/- {scores.std():.4f} (chance={chance:.4f})")
        except Exception as e:
            sklearn_results[clf_name] = {"error": str(e)}

    return {
        "biogpu": {
            "balanced_accuracy": biogpu_result.balanced_accuracy,
            "chance_level": biogpu_result.chance_level,
            "n_reservoir_units": biogpu_result.n_reservoir_units,
            "n_windows": biogpu_result.n_windows,
            "n_features_nsi": biogpu_result.n_features_nsi,
            "n_features_reservoir": biogpu_result.n_features_reservoir,
            "per_class": biogpu_result.per_class_metrics,
        },
        "sklearn": sklearn_results,
        "biogpu_time_s": round(biogpu_time_s, 2),
        "n_windows_total": len(windows),
        "n_windows_valid": len(windows_valid),
    }
