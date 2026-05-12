from biogpu.data.energy_accounting import estimate_system_energy


def test_energy_accounting_structure():
    report = estimate_system_energy({'proxy_score': 10}, task_count=5, seconds=2.0, host_watts=10.0)
    assert report['total_joules'] >= 20.0
    assert report['joules_per_task'] > 0
    assert any(c['name'] == 'life_support' for c in report['components'])
