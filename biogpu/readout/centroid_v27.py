from __future__ import annotations
from collections import defaultdict
from typing import Any, Iterable, List
from biogpu.readout.base_v27 import BioGPUReadout, ReadoutFeatureBatch, ReadoutPrediction, l2_distance, soft_confidence_from_distance

class CentroidReadoutV27:
    decoder_id = "centroid_v27"
    kind = "centroid"

    def __init__(self) -> None:
        self.centroids: dict[Any, list[float]] = {}
        self.feature_names: list[str] = []

    def fit(self, batch: ReadoutFeatureBatch) -> "CentroidReadoutV27":
        batch.validate()
        if batch.y is None:
            raise ValueError("CentroidReadoutV27 requires labels")
        sums: dict[Any, list[float]] = {}
        counts: dict[Any, int] = defaultdict(int)
        for x, y in zip(batch.X, batch.y):
            if y not in sums:
                sums[y] = [0.0] * len(x)
            for i, v in enumerate(x):
                sums[y][i] += float(v)
            counts[y] += 1
        self.centroids = {y: [v / counts[y] for v in s] for y, s in sums.items()}
        self.feature_names = list(batch.feature_names)
        return self

    def predict_one(self, features: Iterable[float], feature_names: List[str] | None = None) -> ReadoutPrediction:
        if not self.centroids:
            raise RuntimeError("CentroidReadoutV27 is not fitted")
        x = [float(v) for v in features]
        distances = {str(y): l2_distance(x, c) for y, c in self.centroids.items()}
        ordered = sorted(distances.items(), key=lambda kv: kv[1])
        pred_s, best = ordered[0]
        second = ordered[1][1] if len(ordered) > 1 else None
        # recover original label type where possible
        pred = next((y for y in self.centroids if str(y) == pred_s), pred_s)
        conf = soft_confidence_from_distance(best, second)
        scores = {k: -v for k, v in distances.items()}
        return ReadoutPrediction(self.decoder_id, pred, conf, scores, {"distance_best": best, "distance_second": second})
