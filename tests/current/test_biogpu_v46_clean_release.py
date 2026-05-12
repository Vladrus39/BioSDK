from pathlib import Path
import json

from biogpu.datasets.asset_integration_v46 import (
    profile_preprocessed_mea_extracted_dir,
    profile_preprocessed_mea_zip,
    validate_asset_against_manifest,
    validate_extracted_asset_against_manifest,
)
from biogpu.release.clean_release_v46 import build_v46_summary, get_powerpc_deferred_items_v46


def test_v46_sample_asset_exists_and_profiles():
    sample = Path('data/samples/zenodo_14363732_preprocessed_sample.zip')
    profile = profile_preprocessed_mea_zip(sample)
    assert profile.exists
    assert profile.electrode_csv_count >= 1
    assert profile.metadata_csv_count >= 1
    assert profile.recording_count >= 1


def test_v46_full_asset_manifest_present():
    manifest = Path('data/assets/zenodo_14363732_preprocessed.asset.json')
    assert manifest.exists()
    data = json.loads(manifest.read_text())
    assert data['include_full_archive_in_sdk'] is False
    assert data['sha256'] == '502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6'
    assert data['recording_count'] >= 50


def test_v46_sample_manifest_validates_against_sample():
    sample = Path('data/samples/zenodo_14363732_preprocessed_sample.zip')
    manifest = Path('data/assets/zenodo_14363732_preprocessed_sample.asset.json')
    result = validate_asset_against_manifest(sample, manifest)
    assert result['valid']


def test_v46_extracted_full_dataset_profiles_against_manifest_when_present():
    extracted = Path('Pre_processed_MEA_data')
    if not extracted.exists():
        return
    manifest = Path('data/assets/zenodo_14363732_preprocessed.asset.json')
    profile = profile_preprocessed_mea_extracted_dir(extracted)
    result = validate_extracted_asset_against_manifest(extracted, manifest)
    assert profile.recording_count >= 50
    assert result['valid']
    assert result['validation_level'] == 'extracted_content_profile_only'
    assert result['does_not_validate_original_zip_hash'] is True


def test_v46_deferred_powerpc_items_include_full_shuffle_and_raw_hdf5():
    items = get_powerpc_deferred_items_v46()
    titles = ' '.join(x.title for x in items).lower()
    assert 'full_shuffle_1000' in titles
    assert 'raw hdf5' in titles
    assert any(x.required_before_beta for x in items)


def test_v46_release_summary_blocks_live_actuation():
    summary = build_v46_summary()
    assert summary['policy']['live_actuation'] == 'blocked_by_default'
    assert summary['policy']['historical_outputs_embedded'] is False
