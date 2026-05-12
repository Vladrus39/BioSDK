from __future__ import annotations
from collections import defaultdict
from typing import Any, Iterable, List
from biogpu.readout.base_v27 import ReadoutFeatureBatch, ReadoutPrediction
from biogpu.readout.centroid_v27 import CentroidReadoutV27

class OnlineCentroidReadoutV27(CentroidReadoutV27):
    decoder_id = "online_centroid_v27"
    kind = "online_centroid"

    def partial_fit_one(self, features: Iterable[float], label: Any) -> "OnlineCentroidReadoutV27":
        x = [float(v) for v in features]
        if label not in self.centroids:
            self.centroids[label] = x
            self._counts = getattr(self, "_counts", {})
            self._counts[label] = 1
            return self
        self._counts = getattr(self, "_counts", {})
        n = self._counts.get(label, 1)
        old = self.centroids[label]
        self.centroids[label] = [(old_i * n + x_i) / (n + 1) for old_i, x_i in zip(old, x)]
        self._counts[label] = n + 1
        return self
