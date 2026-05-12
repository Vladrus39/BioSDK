from biogpu.data_ingest.dandi_discovery import candidates_as_dict, keyword_score


def test_dandi_candidates_include_000469():
    ids = {c["dandiset_id"] for c in candidates_as_dict()}
    assert "000469" in ids


def test_keyword_score_finds_ecephys_terms():
    assert keyword_score({"description": "NWB extracellular ecephys units stimulus behavior"}) >= 4
