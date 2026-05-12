from biogpu.data_ingest.brc2602_import import minimal_brc2602_contract

def test_brc2602_contract_has_required_fields():
    c=minimal_brc2602_contract(); assert 'spike_source' in c and 'stimulus_table' in c and 'electrode_map' in c
