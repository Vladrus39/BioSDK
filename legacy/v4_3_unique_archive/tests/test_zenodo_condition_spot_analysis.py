from biogpu.analysis.zenodo_condition_spot import electrode_distance, spot_level_summary


def test_electrode_distance_grid():
    assert electrode_distance(34, 34) == 0
    assert electrode_distance(34, 35) == 1
    assert electrode_distance(34, 44) == 1


def test_spot_level_summary_empty():
    s = spot_level_summary([])
    assert s['lightstim_recordings_with_baseline'] == 0
