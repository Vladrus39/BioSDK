from biogpu.benchmarks.delayed_match import main


def test_delayed_match_benchmark_runs():
    result = main('configs/delayed_match.yaml')
    assert result['benchmark'] == 'delayed_match_memory'
    assert 'accuracy' in result['metrics']
    assert 'last_frame_only_raw_linear' in result['baselines']
