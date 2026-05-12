from biogpu.benchmarks.sequence import main


def test_sequence_benchmark_runs():
    results = main('configs/sequence.yaml')
    assert 'metrics' in results
    assert 0.0 <= results['metrics']['accuracy'] <= 1.0
