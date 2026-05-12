import numpy as np

from biogpu.integration.realdata_replay_v32 import RealDataMatrixV32
from biogpu.statistics.lineage_split_v36 import parse_culture_lineage_v36, build_lineage_strict_splits_v36
from biogpu.statistics.bootstrap_v36 import bootstrap_mean_ci_v36


def _tiny_matrix():
    # Same base lineages appear at multiple DIV labels; v3.6 must not split them across train/test.
    cultures = np.array([
        "40628_13DIV", "40628_18DIV", "40628_21DIV", "39566_21DIV", "39566_24DIV", "41438_19DIV", "41438_20DIV", "40323_18DIV"
    ] * 4, dtype=str)
    y = np.array(([1,1,2,1,2,1,2,2] * 4), dtype=int)
    X = np.arange(len(y)*6, dtype=float).reshape(len(y), 6)
    return RealDataMatrixV32(
        X=X,
        y=y,
        cultures=cultures,
        conditions=np.array(["LightStim"]*len(y), dtype=str),
        recording_path=np.array(["r"]*len(y), dtype=str),
        pulse_index=np.arange(len(y), dtype=int),
        feature_names=[f"response_delta_count_e{i}" for i in range(6)],
        source_path="tiny",
    )


def test_parse_culture_lineage_v36():
    p = parse_culture_lineage_v36("40628_21DIV")
    assert p.base_lineage_id == "40628"
    assert p.div == 21
    assert p.parser_status == "base_plus_div"


def test_lineage_split_has_no_base_leakage():
    m = _tiny_matrix()
    splits = build_lineage_strict_splits_v36(m, split_offsets=(0,1), heldout_lineage_count=1)
    assert splits
    for s in splits:
        assert s.leakage_check_passed is True
        train_lineages = {parse_culture_lineage_v36(m.cultures[i]).base_lineage_id for i in s.train_idx}
        test_lineages = {parse_culture_lineage_v36(m.cultures[i]).base_lineage_id for i in s.test_idx}
        assert train_lineages.isdisjoint(test_lineages)


def test_bootstrap_ci_contains_mean():
    ci = bootstrap_mean_ci_v36([0.1, 0.2, 0.3, 0.4], iterations=100, seed=36)
    assert ci.n == 4
    assert ci.low <= ci.mean <= ci.high
    assert ci.confidence == 0.95
