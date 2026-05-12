from pathlib import Path
from biogpu.powerpc.runner_plan_v34 import build_powerpc_package_v34, write_powerpc_outputs_v34


def test_v34_package_has_full_shuffle_preset():
    pkg = build_powerpc_package_v34()
    ids = {p.preset_id for p in pkg.presets}
    assert 'full_shuffle_1000' in ids
    assert 'smoke' in ids


def test_v34_presets_have_expected_boundaries():
    pkg = build_powerpc_package_v34()
    full = [p for p in pkg.presets if p.preset_id == 'full_shuffle_1000'][0]
    assert full.shuffle_count >= 1000
    assert full.expected_run_count > 0
    assert 'GPU advantage' in ' '.join(pkg.lab_only_future) or pkg.lab_only_future


def test_v34_outputs_are_written(tmp_path):
    summary = write_powerpc_outputs_v34(tmp_path)
    assert summary['status'] == 'completed_powerpc_transfer_package'
    assert summary['live_output_performed'] is False
    assert summary['gpu_advantage_claimed'] is False
    assert (tmp_path / 'v34_powerpc_manifest.json').exists()
    assert (tmp_path / 'BIOGPU_V34_POWERPC_RUNNER_GUIDE.md').exists()
    assert (tmp_path / 'biogpu_v34_powerpc_runner_bundle.zip').exists()
