import numpy as np
from biogpu.data.memory_metrics import reservoir_memory_report, class_centroid_separability, temporal_trace_score


def test_memory_report_has_scores():
    X = np.array([[1,0],[0.9,0.1],[0,1],[0.1,0.9]], dtype=float)
    y = np.array([0,0,1,1])
    report = reservoir_memory_report(X, y)
    assert report["num_states"] == 4
    assert report["num_features"] == 2
    assert report["class_centroid_separability"] > 0


def test_temporal_trace_score_range():
    X = np.eye(4)
    score = temporal_trace_score(X)
    assert -1.0 <= score <= 1.0
