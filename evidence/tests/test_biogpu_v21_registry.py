from biogpu.benchmarks.registry_v21 import build_v21_benchmark_registry


def test_registry_contains_main_benchmarks():
    reg = build_v21_benchmark_registry()
    ids = {b.benchmark_id for b in reg.benchmarks}
    assert {'B0_target_vs_random_electrode', 'B4_adaptive_closed_loop', 'B5_energy_per_task'}.issubset(ids)


def test_registry_preserves_claim_boundary():
    reg = build_v21_benchmark_registry()
    assert 'GPU-advantage' in reg.claim_boundary
    assert any(b.live_required for b in reg.benchmarks)
    assert any(b.heavy_compute for b in reg.benchmarks)


def test_energy_task_requires_live_measurement():
    reg = build_v21_benchmark_registry()
    b5 = next(b for b in reg.benchmarks if b.benchmark_id == 'B5_energy_per_task')
    assert b5.live_required
    assert 'E_task_total' in b5.primary_metrics
