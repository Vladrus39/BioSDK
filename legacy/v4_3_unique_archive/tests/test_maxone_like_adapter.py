from biogpu.substrates import MaxOneLikeDryRunAdapter


def test_maxone_like_contract_is_dry_run():
    adapter = MaxOneLikeDryRunAdapter()
    h = adapter.health_check()
    assert h['dry_run'] is True
    assert h['capabilities']['electrode_count'] == 26400
    assert h['capabilities']['supports_recording'] is True
