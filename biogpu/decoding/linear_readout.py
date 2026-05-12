from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

class LinearReadout:
    def __init__(self, max_iter: int = 1000, random_state: int = 42):
        self.model = make_pipeline(
            StandardScaler(with_mean=True),
            LogisticRegression(max_iter=max_iter, random_state=random_state),
        )

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        return float(self.model.score(X, y))
