from __future__ import annotations

from typing import Any, Iterable, List
import math

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from biogpu.readout.base_v27 import ReadoutFeatureBatch, ReadoutPrediction


def _as_2d(features: Iterable[float]) -> np.ndarray:
    x = np.asarray([float(v) for v in features], dtype=float).reshape(1, -1)
    if not np.all(np.isfinite(x)):
        raise ValueError("features must be finite")
    return x


def _softmax(scores: np.ndarray) -> np.ndarray:
    s = np.asarray(scores, dtype=float)
    if s.ndim == 1:
        s = s.reshape(1, -1)
    s = s - np.max(s, axis=1, keepdims=True)
    exp = np.exp(s)
    return exp / (np.sum(exp, axis=1, keepdims=True) + 1e-12)


class LogisticL2ReadoutV27:
    """Real sklearn-backed L2 logistic readout.

    Earlier v2.7 archives exposed this decoder id with a centroid fallback. v3.5
    makes the decoder real while preserving the public registry id for backwards
    compatibility.
    """
    decoder_id = "logistic_l2_v27"
    kind = "logistic_l2"

    def __init__(self, *, C: float = 1.0, max_iter: int = 2000, random_state: int = 27) -> None:
        self.C = float(C)
        self.max_iter = int(max_iter)
        self.random_state = int(random_state)
        self.pipeline: Pipeline | None = None
        self.feature_names: list[str] = []
        self.classes_: np.ndarray | None = None

    def fit(self, batch: ReadoutFeatureBatch) -> "LogisticL2ReadoutV27":
        batch.validate()
        if batch.y is None:
            raise ValueError("LogisticL2ReadoutV27 requires labels")
        X = np.asarray(batch.X, dtype=float)
        y = np.asarray(batch.y)
        if len(set(map(str, y))) < 2:
            raise ValueError("LogisticL2ReadoutV27 requires at least two classes")
        clf = LogisticRegression(
            C=self.C,
            solver="lbfgs",
            max_iter=self.max_iter,
            random_state=self.random_state,
        )
        self.pipeline = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
        self.pipeline.fit(X, y)
        self.classes_ = self.pipeline.named_steps["clf"].classes_
        self.feature_names = list(batch.feature_names)
        return self

    def predict_one(self, features: Iterable[float], feature_names: List[str] | None = None) -> ReadoutPrediction:
        if self.pipeline is None or self.classes_ is None:
            raise RuntimeError("LogisticL2ReadoutV27 is not fitted")
        x = _as_2d(features)
        pred = self.pipeline.predict(x)[0]
        if hasattr(self.pipeline.named_steps["clf"], "predict_proba"):
            proba = self.pipeline.predict_proba(x)[0]
        else:
            proba = _softmax(self.pipeline.decision_function(x))[0]
        scores = {str(cls): float(p) for cls, p in zip(self.classes_, proba)}
        confidence = float(np.max(proba)) if len(proba) else None
        return ReadoutPrediction(self.decoder_id, pred.item() if hasattr(pred, "item") else pred, confidence, scores, {
            "model": "sklearn.linear_model.LogisticRegression",
            "scaler": "StandardScaler",
            "real_sklearn_model": True,
        })


class LinearSVMReadoutV27:
    """Real sklearn-backed LinearSVC readout with decision-score confidence."""
    decoder_id = "linear_svm_v27"
    kind = "linear_svm"

    def __init__(self, *, C: float = 1.0, max_iter: int = 5000, random_state: int = 27) -> None:
        self.C = float(C)
        self.max_iter = int(max_iter)
        self.random_state = int(random_state)
        self.pipeline: Pipeline | None = None
        self.feature_names: list[str] = []
        self.classes_: np.ndarray | None = None

    def fit(self, batch: ReadoutFeatureBatch) -> "LinearSVMReadoutV27":
        batch.validate()
        if batch.y is None:
            raise ValueError("LinearSVMReadoutV27 requires labels")
        X = np.asarray(batch.X, dtype=float)
        y = np.asarray(batch.y)
        if len(set(map(str, y))) < 2:
            raise ValueError("LinearSVMReadoutV27 requires at least two classes")
        clf = LinearSVC(C=self.C, max_iter=self.max_iter, random_state=self.random_state, dual="auto")
        self.pipeline = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
        self.pipeline.fit(X, y)
        self.classes_ = self.pipeline.named_steps["clf"].classes_
        self.feature_names = list(batch.feature_names)
        return self

    def predict_one(self, features: Iterable[float], feature_names: List[str] | None = None) -> ReadoutPrediction:
        if self.pipeline is None or self.classes_ is None:
            raise RuntimeError("LinearSVMReadoutV27 is not fitted")
        x = _as_2d(features)
        pred = self.pipeline.predict(x)[0]
        raw = self.pipeline.decision_function(x)
        if np.asarray(raw).ndim == 1 and len(self.classes_) == 2:
            margin = float(np.asarray(raw).reshape(-1)[0])
            # LinearSVC binary decision_function is signed distance to class[1].
            scores_arr = np.asarray([[-margin, margin]], dtype=float)
        else:
            scores_arr = np.asarray(raw, dtype=float).reshape(1, -1)
        probs = _softmax(scores_arr)[0]
        scores = {str(cls): float(score) for cls, score in zip(self.classes_, scores_arr[0])}
        confidence = float(np.max(probs)) if len(probs) else None
        return ReadoutPrediction(self.decoder_id, pred.item() if hasattr(pred, "item") else pred, confidence, scores, {
            "model": "sklearn.svm.LinearSVC",
            "scaler": "StandardScaler",
            "real_sklearn_model": True,
            "confidence_note": "softmax over decision scores; not calibrated probability",
        })
