from biogpu.data_ingest.zenodo_manifest import zenodo_manifest_dict, recommended_downloads

def test_zenodo_manifest_contains_preprocessed():
    m=zenodo_manifest_dict(); names=[f['filename'] for f in m['files']]
    assert 'Pre_processed_MEA_data.zip' in names
    assert m['record_id']=='14363732'

def test_recommended_downloads_small():
    rec=recommended_downloads()
    assert any(f['filename']=='Pre_processed_MEA_data.zip' for f in rec)
    assert all(f['size_mb']<=200 for f in rec)
