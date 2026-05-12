from biogpu.beta.master_plan_v45 import access_tiers, cleanup_items, dataset_sources, roadmap_items
from biogpu.enterprise.security_data_v45 import data_handling_rules


def test_master_plan_has_power_pc_and_lab_items():
    items = roadmap_items()
    phases = {i.phase for i in items}
    assert "power_pc" in phases
    assert "lab_validation" in phases
    assert any("full_shuffle_1000" in i.title for i in items)
    assert any("Zenodo raw HDF5" in i.title for i in items)


def test_access_policy_is_maximum_safe_access_not_tiny_demo():
    tiers = access_tiers()
    research = next(t for t in tiers if t.tier == "Research/Lab Evaluation")
    assert "own data upload/import" in research.allowed
    assert "result bundle export" in research.allowed
    assert "unapproved live stimulation" in research.blocked


def test_dataset_sources_include_required_expansion():
    ids = {d.id for d in dataset_sources()}
    assert "zenodo_14363732_raw_hdf5" in ids
    assert "dandi_nwb_discovery" in ids
    assert "allen_visual_coding_orientation" in ids
    assert "user_uploaded_neural_data" in ids


def test_cleanup_audit_admits_document_sprawl():
    problems = "\n".join(i.problem for i in cleanup_items())
    assert "spread" in problems or "clutter" in problems


def test_security_rules_block_live_actuation_by_default():
    rules = data_handling_rules()
    assert any("Live actuation is blocked" in r.rule for r in rules)
