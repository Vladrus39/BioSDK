from biogpu.api.server import app


def test_api_registered():
    routes = {r.path for r in app.routes}
    assert '/benchmarks/noise' in routes
    assert '/benchmarks/sequence' in routes
    assert '/benchmarks/delayed-match' in routes
    assert '/benchmarks/ablation' in routes
    assert '/public-data/dandi-candidates' in routes
    assert '/public-data/task-aligned-contract' in routes
