from pathlib import Path
from biogpu.data.plots import plot_metric_bars


def test_plot_metric_bars(tmp_path):
    p = tmp_path / 'bars.png'
    plot_metric_bars({'a': 0.1, 'b': 0.2}, p)
    assert p.exists()
