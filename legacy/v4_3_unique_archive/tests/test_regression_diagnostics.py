from biogpu.diagnostics import diagnose_reservoir_signal, aggregate_metric, summarize_runs


def test_regression_diagnostic_flags_bad_result():
    result = {
        "benchmark": "orientation",
        "metrics": {"accuracy": 0.17},
        "baselines": {"shuffled_reservoir": 0.27, "random_features": 0.34, "raw_linear": 1.0},
    }
    diag = diagnose_reservoir_signal(result)
    assert diag.severity == "red"
    assert diag.reservoir_margin_vs_shuffled < 0


def test_aggregate_metric_and_summary():
    m = aggregate_metric([0.4, 0.5, 0.6], "accuracy")
    assert m.count == 3
    assert round(m.mean, 2) == 0.5
    summary = summarize_runs([
        {"metrics": {"accuracy": 0.4}, "baselines": {"shuffled": 0.3}},
        {"metrics": {"accuracy": 0.6}, "baselines": {"shuffled": 0.4}},
    ])
    assert summary["runs"] == 2
    assert "shuffled" in summary["baselines"]
