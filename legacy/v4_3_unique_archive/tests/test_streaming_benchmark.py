from biogpu.benchmarks.streaming import main


def test_streaming_benchmark_runs():
    result = main('configs/streaming.yaml')
    assert result['benchmark'] == 'streaming_change'
    assert 'metrics' in result and 'accuracy' in result['metrics']
    assert 'energy_accounting' in result
