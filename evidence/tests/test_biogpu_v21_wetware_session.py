from pathlib import Path
from biogpu.wetware.provisional_stack_v21 import build_provisional_wetware_stack_v21, write_wetware_outputs_v21
from biogpu.runtime.session_v21 import default_v21_session, write_session_file, collect_result_bundle


def test_wetware_stack_has_media_and_coating_layers():
    spec = build_provisional_wetware_stack_v21()
    text = ' '.join(c.ideal_choice for c in spec.components).lower()
    assert 'brainphys' in text
    assert 'neurobasal' in text
    assert 'laminin' in text
    assert 'pdl' in text or 'pei' in text
    assert 'No exact concentrations' in spec.explicit_non_protocol_boundary[0]


def test_session_schema_default_power_pc():
    s = default_v21_session('power_pc_full')
    assert s.mode == 'power_pc_full'
    assert 'logistic_l2' in s.readouts
    assert s.safety_class == 'offline_or_dry_run_only'


def test_wetware_outputs_and_bundle(tmp_path: Path):
    out = tmp_path / 'out'
    wet = write_wetware_outputs_v21(out)
    assert wet['components'] >= 6
    s = default_v21_session('replay_local')
    write_session_file(s, out)
    bundle = collect_result_bundle(s, [out], out)
    assert Path(bundle['bundle_path']).exists()
    assert bundle['file_count'] >= 2
