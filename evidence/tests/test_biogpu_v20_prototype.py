from biogpu.runtime.prototype_v20 import (
    build_connection_map_v20,
    build_lab_boundaries_v20,
    build_prototype_stack_v20,
    build_visual_spec_v20,
)


def test_visual_spec_mentions_living_neural_cartridge():
    names = {x.name for x in build_visual_spec_v20()}
    assert 'Living neural cartridge' in names


def test_connection_map_has_runtime_path():
    steps = build_connection_map_v20()
    assert any(x.component == 'BioGPU runtime' and x.connects_to == 'Feature extraction / readout' for x in steps)
    assert len(steps) >= 8


def test_lab_boundaries_are_explicit():
    boundaries = build_lab_boundaries_v20()
    flat = ' '.join(' '.join(x.not_included_here) for x in boundaries).lower()
    assert 'wet-lab' in flat or 'culturing' in flat
    assert 'recipes' in flat or 'concentrations' in flat


def test_v20_stack_keeps_biogpu_goal():
    stack = build_prototype_stack_v20()
    assert 'biological computing accelerator' in stack.goal
    assert 'MEA/HD-MEA' in stack.first_real_form
