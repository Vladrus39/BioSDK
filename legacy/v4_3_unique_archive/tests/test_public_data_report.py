from biogpu.data_ingest.public_data_report import build_public_data_status_report

def test_public_data_report_mentions_honesty_rule():
    txt=build_public_data_status_report()
    assert 'Honesty rule' in txt and 'Zenodo 14363732' in txt and 'DANDI' in txt
