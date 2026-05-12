from biogpu.benchmarks.ablation import main


def test_ablation_benchmark_runs():
    result = main('configs/ablation.yaml')
    assert result['benchmark'] == 'reservoir_ablation'
    assert 'normal_v1_reservoir' in result['ablations']
    assert 'no_recurrent_memory' in result['ablations']
