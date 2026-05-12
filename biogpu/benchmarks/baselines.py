from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


def raw_linear_baseline(X_train_raw, y_train, X_test_raw, y_test, seed=42):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=seed))
    model.fit(X_train_raw, y_train)
    return float(model.score(X_test_raw, y_test))


def raw_mlp_baseline(X_train_raw, y_train, X_test_raw, y_test, seed=42):
    model = make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(32,), max_iter=300, random_state=seed))
    model.fit(X_train_raw, y_train)
    return float(model.score(X_test_raw, y_test))


def shuffled_reservoir_score(readout_cls, X_train, y_train, X_test, y_test, seed=42):
    rng = np.random.default_rng(seed)
    X_train_shuf = X_train.copy()
    rng.shuffle(X_train_shuf, axis=0)
    model = readout_cls()
    model.fit(X_train_shuf, y_train)
    return model.score(X_test, y_test)


def random_feature_baseline(readout_cls, X_train, y_train, X_test, y_test, seed=42):
    rng = np.random.default_rng(seed)
    train = rng.normal(size=X_train.shape)
    test = rng.normal(size=X_test.shape)
    model = readout_cls()
    model.fit(train, y_train)
    return model.score(test, y_test)
