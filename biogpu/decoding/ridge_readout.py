from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

class RidgeReadout:
    def __init__(self):
        self.model = make_pipeline(StandardScaler(with_mean=True), RidgeClassifier())
    def fit(self, X, y):
        self.model.fit(X, y); return self
    def predict(self, X):
        return self.model.predict(X)
    def score(self, X, y):
        return float(self.model.score(X, y))
