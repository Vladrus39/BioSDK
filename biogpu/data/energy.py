from __future__ import annotations
import numpy as np


def estimate_energy_proxy(event_counts, spike_counts, active_ratios, readout_features: int | None = None) -> dict:
    """Compute transparent proxy metrics, not real joules.

    Real biological energy must include host, MEA, stimulator and life-support.
    This proxy is only for comparing software pipelines before lab hardware.
    """
    event_counts = np.asarray(event_counts, dtype=float)
    spike_counts = np.asarray(spike_counts, dtype=float)
    active_ratios = np.asarray(active_ratios, dtype=float)
    readout_features = int(readout_features or 0)
    return {
        "mean_event_count": float(np.mean(event_counts)) if event_counts.size else 0.0,
        "mean_spike_count": float(np.mean(spike_counts)) if spike_counts.size else 0.0,
        "mean_active_ratio": float(np.mean(active_ratios)) if active_ratios.size else 0.0,
        "readout_features": readout_features,
        "proxy_score": float((np.mean(event_counts) if event_counts.size else 0.0) + (np.mean(spike_counts) if spike_counts.size else 0.0) + 0.01 * readout_features),
        "note": "Proxy only: not joules. Real BioGPU accounting must include host + MEA + stimulator + life-support.",
    }
