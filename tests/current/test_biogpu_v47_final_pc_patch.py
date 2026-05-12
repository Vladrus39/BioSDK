from pathlib import Path
from biogpu.release.final_pc_patch_v47 import validate_v47_project, get_first_72h_steps_v47, get_v47_patch_policy


def test_v47_policy_blocks_live_control():
    policy = get_v47_patch_policy()
    assert policy['unsafe_live_control'] == 'blocked_by_default'
    assert policy['heavy_scripts_are_placeholders'] is False


def test_first_72h_steps_include_heavy_runs():
    steps = get_first_72h_steps_v47()
    commands = '\n'.join(s.command for s in steps)
    assert 'full_shuffle_1000' in commands
    assert 'extended_methods_5000' in commands
    assert 'Pre_processed_MEA_data.zip' in commands


def test_v47_project_validate_current_tree():
    result = validate_v47_project('.')
    assert result['ready_for_power_pc_handoff'], result
    assert not result['missing_paths']
    assert not result['todo_scripts']


def test_required_evidence_matrix_present():
    assert Path('evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz').exists()


def test_beta_docs_restored():
    assert Path('beta/BETA_TESTER_CHECKLIST.md').exists()
    assert Path('beta/PRIVATE_BETA_ACCEPTANCE_CRITERIA.md').exists()
