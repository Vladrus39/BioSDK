from __future__ import annotations

import numpy as np
from biogpu.schemas import SpikeTrain, FeatureVector


class BasicSpikeFeatureExtractor:
    """Converts spike trains into fixed-width feature vectors.

    v0.4 adds optional configurable readout windows (`readout_bins`). When bins
    are enabled, the feature vector includes time-binned spike counts in addition
    to total counts and latency. Default behavior remains backward compatible.
    """

    def __init__(self, num_units: int = 256, window_ms: float = 20.0, readout_bins: int = 1):
        self.num_units = int(num_units)
        self.window_ms = float(window_ms)
        self.readout_bins = max(1, int(readout_bins))

    def transform(self, spike_train: SpikeTrain) -> FeatureVector:
        counts = np.zeros(self.num_units, dtype=np.float32)
        latency = np.ones(self.num_units, dtype=np.float32) * self.window_ms
        binned = np.zeros((self.readout_bins, self.num_units), dtype=np.float32)
        bin_width = self.window_ms / float(self.readout_bins)

        for unit, t in zip(spike_train.unit_ids, spike_train.spike_times):
            idx = int(unit) % self.num_units
            t = float(t)
            counts[idx] += 1.0
            latency[idx] = min(latency[idx], t)
            if self.readout_bins > 1:
                b = min(self.readout_bins - 1, max(0, int(t // max(bin_width, 1e-9))))
                binned[b, idx] += 1.0

        active_ratio = np.array([np.mean(counts > 0)], dtype=np.float32)
        total_spikes = np.array([np.sum(counts)], dtype=np.float32)
        mean_latency = np.array([np.mean(latency[counts > 0]) if np.any(counts > 0) else self.window_ms], dtype=np.float32)

        values_parts = [counts, latency / self.window_ms]
        names = [f"count_{i}" for i in range(self.num_units)] + [f"latency_{i}" for i in range(self.num_units)]
        if self.readout_bins > 1:
            values_parts.append(binned.reshape(-1))
            names.extend([f"bin_{b}_count_{i}" for b in range(self.readout_bins) for i in range(self.num_units)])
        values_parts.extend([active_ratio, total_spikes, mean_latency])
        names += ["active_ratio", "total_spikes", "mean_latency"]
        values = np.concatenate(values_parts)
        return FeatureVector(
            values=values,
            names=names,
            metadata={
                "extractor": "BasicSpikeFeatureExtractor",
                "window_ms": self.window_ms,
                "readout_bins": self.readout_bins,
            },
        )
