from biogpu.benchmarks.noise import main


def test_noise_benchmark_runs():
    results = main('configs/noise.yaml')
    assert 'metrics' in results
    assert 'noise_curve' in results
    assert 0.0 <= results['metrics']['accuracy'] <= 1.0
