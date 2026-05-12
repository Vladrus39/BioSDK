"""BioGPU Core v2.0 — Feature extraction.

Extracts 20 universal features from any time-series neural data.
Features are grouped into 5 categories for ablation studies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy import stats, signal
from sklearn.preprocessing import StandardScaler

FEATURE_GROUPS = {
    "amplitude": ["mean_amplitude", "std_amplitude", "peak_to_peak", "rms"],
    "temporal": ["zero_crossing_rate", "line_length", "skewness", "kurtosis"],
    "spectral": ["delta_power", "theta_power", "alpha_power", "beta_power", "gamma_power"],
    "complexity": ["sample_entropy", "hjorth_mobility", "hjorth_complexity", "hurst_exponent"],
    "connectivity": ["channel_correlation_mean", "channel_correlation_std", "phase_sync_mean"],
}

FEATURE_NAMES = [f for group in FEATURE_GROUPS.values() for f in group]


@dataclass
class FeatureResult:
    features: np.ndarray  # (n_windows, n_features)
    feature_names: list[str] = field(default_factory=lambda: FEATURE_NAMES)
    group_names: list[str] = field(default_factory=list)
    window_size: int = 0
    n_windows: int = 0
    n_channels: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


def extract_features(
    data: np.ndarray,
    sample_rate_hz: float = 1000.0,
    window_size_seconds: float = 1.0,
    window_overlap: float = 0.5,
    groups: list[str] | None = None,
) -> FeatureResult:
    """Extract features from multi-channel time-series data.

    Args:
        data: (channels, samples) array
        sample_rate_hz: sampling rate
        window_size_seconds: sliding window size
        window_overlap: fraction of overlap between windows (0-1)
        groups: which feature groups to compute (None = all)

    Returns:
        FeatureResult with (n_windows, n_features) matrix
    """
    if data is None or data.size == 0:
        return FeatureResult(features=np.zeros((0, len(FEATURE_NAMES))))

    n_channels, n_samples = data.shape
    window_samples = int(window_size_seconds * sample_rate_hz)
    step_samples = int(window_samples * (1 - window_overlap))
    if window_samples < 4 or step_samples < 1:
        window_samples = min(n_samples, max(4, n_samples // 10))
        step_samples = window_samples // 2

    n_windows = max(1, (n_samples - window_samples) // step_samples + 1)

    all_features = []
    for w in range(n_windows):
        start = w * step_samples
        end = min(start + window_samples, n_samples)
        window = data[:, start:end]
        feats = _extract_window_features(window, sample_rate_hz, groups)
        all_features.append(feats)

    features = np.array(all_features)

    # Handle NaN/Inf
    features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

    # Scale
    if features.size > 0:
        features = StandardScaler().fit_transform(features)

    result = FeatureResult(
        features=features,
        window_size=window_samples,
        n_windows=n_windows,
        n_channels=n_channels,
    )
    result.group_names = FEATURE_NAMES  # Use FEATURE_NAMES from module level
    return result


def _extract_window_features(
    window: np.ndarray,
    sample_rate_hz: float,
    groups: list[str] | None = None,
) -> list[float]:
    """Extract features from a single window."""
    feats: list[float] = []
    active_groups = set(groups) if groups else set(FEATURE_GROUPS.keys())

    n_channels = window.shape[0]

    # Per-channel features averaged
    ch_means = np.mean(window, axis=1)
    ch_stds = np.std(window, axis=1)
    ch_ptps = np.ptp(window, axis=1)

    if "amplitude" in active_groups:
        feats.append(float(np.mean(ch_means)))
        feats.append(float(np.mean(ch_stds)))
        feats.append(float(np.mean(ch_ptps)))
        feats.append(float(np.sqrt(np.mean(window**2))))

    if "temporal" in active_groups:
        zcr = np.mean([((window[i, :-1] * window[i, 1:]) < 0).sum() / len(window[i])
                        for i in range(n_channels)]) if n_channels > 0 else 0.0
        ll = np.mean([np.sum(np.abs(np.diff(window[i]))) for i in range(n_channels)])
        sk = float(np.mean(stats.skew(window, axis=1)))
        ku = float(np.mean(stats.kurtosis(window, axis=1)))
        feats.extend([float(zcr), float(ll), sk, ku])

    if "spectral" in active_groups:
        bands = {"delta": (0.5, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30), "gamma": (30, 100)}
        for band in ["delta", "theta", "alpha", "beta", "gamma"]:
            low, high = bands[band]
            low_bin = max(0, int(low * window.shape[1] / sample_rate_hz))
            high_bin = min(window.shape[1] - 1, int(high * window.shape[1] / sample_rate_hz))
            if high_bin > low_bin:
                power = np.mean(np.abs(np.fft.rfft(window, axis=1)[:, low_bin:high_bin])**2)
            else:
                power = 0.0
            feats.append(float(power))

    if "complexity" in active_groups:
        # Sample entropy (simplified)
        entropies = []
        for i in range(min(n_channels, 4)):
            diffs = np.abs(np.diff(window[i]))
            if len(diffs) > 1:
                m = np.mean(diffs)
                r = 0.2 * np.std(diffs) if np.std(diffs) > 0 else 0.001
                a = np.sum(np.abs(diffs[:-1] - diffs[1:]) < r) / max(1, len(diffs) - 1)
                b = np.sum(np.abs(diffs) < r) / max(1, len(diffs))
                se = -np.log(a / b) if a > 0 and b > 0 else 0.0
            else:
                se = 0.0
            entropies.append(min(se, 10.0))
        feats.append(float(np.mean(entropies)) if entropies else 0.0)

        # Hjorth parameters
        for i in range(min(n_channels, 1)):
            ch = window[i]
            d1 = np.diff(ch)
            d2 = np.diff(d1)
            mob = np.sqrt(np.var(d1) / np.var(ch)) if np.var(ch) > 0 else 0.0
            com = np.sqrt(np.var(d2) / np.var(d1)) / mob if np.var(d1) > 0 and mob > 0 else 0.0
            feats.append(float(mob))
            feats.append(float(com))
        if n_channels < 2:
            feats.extend([0.0, 0.0])

        # Hurst (simplified R/S)
        for i in range(min(n_channels, 1)):
            ch = window[i][:min(len(window[i]), 256)]
            if len(ch) > 4:
                cumsum = np.cumsum(ch - np.mean(ch))
                r = np.max(cumsum) - np.min(cumsum)
                s = np.std(ch) if np.std(ch) > 0 else 1.0
                hurst = np.log(r / s) / np.log(len(ch)) if r > 0 else 0.5
            else:
                hurst = 0.5
            feats.append(float(hurst))
        if n_channels < 2:
            feats.append(0.0)

    if "connectivity" in active_groups and n_channels >= 2:
        corr = np.corrcoef(window)
        triu = corr[np.triu_indices(n_channels, k=1)]
        feats.append(float(np.mean(np.abs(triu))) if len(triu) > 0 else 0.0)
        feats.append(float(np.std(np.abs(triu))) if len(triu) > 0 else 0.0)
        # Phase sync (simplified — mean phase difference)
        hilbert = signal.hilbert(window, axis=1)
        phases = np.angle(hilbert)
        phase_diffs = []
        for i in range(n_channels - 1):
            phase_diffs.append(np.mean(np.abs(phases[i] - phases[i + 1])))
        feats.append(float(np.mean(phase_diffs)) if phase_diffs else 0.0)
    else:
        feats.extend([0.0, 0.0, 0.0])

    return feats
