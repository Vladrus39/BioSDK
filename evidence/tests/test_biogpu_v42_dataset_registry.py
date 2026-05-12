from biogpu.datasets.registry_v42 import build_default_dataset_registry_v42, DatasetAccessModeV42
from biogpu.datasets.importers_v42 import DatasetImportRequestV42, build_importer_catalog_v42


def test_default_registry_valid_and_nonempty():
    registry = build_default_dataset_registry_v42()
    assert len(registry.entries) >= 7
    assert registry.validate() == []
    assert len(registry.by_priority("P0")) >= 2


def test_registry_has_required_beta_sources():
    registry = build_default_dataset_registry_v42()
    required = {
        "zenodo_14363732_preprocessed",
        "zenodo_14363732_raw_hdf5",
        "dandi_nwb_discovery",
        "allen_visual_coding_orientation",
        "finalspark_readonly_export",
        "user_uploaded_neural_data",
    }
    assert required.issubset(set(registry.entries.keys()))


def test_importer_catalog_matches_registry():
    registry = build_default_dataset_registry_v42()
    catalog = build_importer_catalog_v42()
    for entry in registry.entries.values():
        assert entry.import_plan.importer_id in catalog


def test_importers_are_readonly_and_no_live_control():
    registry = build_default_dataset_registry_v42()
    catalog = build_importer_catalog_v42()
    for entry in registry.entries.values():
        imp = catalog[entry.import_plan.importer_id]
        mode = entry.access_mode.value
        opts = {"read_only_token_expected": True} if entry.import_plan.importer_id == "finalspark_export_v42" else {}
        req = DatasetImportRequestV42(entry.dataset_id, entry.import_plan.importer_id, "registry://test", mode=mode, options=opts)
        result = imp.inspect(req)
        assert result.live_control_performed is False
        assert result.status in {"metadata_ready", "blocked"}
        assert not any("live_control" in w and "not allowed" in w for w in result.warnings)


def test_unsafe_import_payload_is_blocked():
    catalog = build_importer_catalog_v42()
    imp = catalog["zenodo_preprocessed_v42"]
    req = DatasetImportRequestV42(
        dataset_id="zenodo_14363732_preprocessed",
        importer_id="zenodo_preprocessed_v42",
        source_uri="registry://unsafe",
        mode="read_only_replay",
        options={"voltage": 10},
    )
    result = imp.inspect(req)
    assert result.status == "blocked"
    assert any("voltage" in w.lower() for w in result.warnings)
