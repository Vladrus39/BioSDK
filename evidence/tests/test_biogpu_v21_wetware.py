from biogpu.runtime.wetware_v21 import build_ideal_wetware_stack_v21


def test_v21_stack_contains_real_neurons_and_mea():
    s = build_ideal_wetware_stack_v21()
    text = (s.core_material_statement + ' ' + s.intended_physical_object).lower()
    assert 'living neurons' in text or 'living-neural' in text
    assert 'mea' in text


def test_v21_has_formula_book():
    s = build_ideal_wetware_stack_v21()
    ids = {f.formula_id for f in s.formulas}
    assert {'F02_cell_planning', 'F06_response_delta', 'F09_energy_task'}.issubset(ids)


def test_v21_connections_have_vendor_boundary():
    s = build_ideal_wetware_stack_v21()
    assert any(c.exact_detail_status == 'vendor-specific' for c in s.connections)
    assert 'not a wet-lab operating protocol' in s.boundary_note


def test_v21_geometry_has_planning_dimensions():
    s = build_ideal_wetware_stack_v21()
    names = {g.name for g in s.geometry}
    assert 'electrode_count' in names
    assert 'medium_volume' in names
