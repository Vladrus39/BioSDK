from pathlib import Path
from biogpu.integration.realdata_replay_v32 import load_v15_realdata_matrix_v32
from biogpu.integration.realdata_sweep_v33 import RealDataSweepConfigV33, build_culture_splits_v33, build_feature_ablations_v33, run_realdata_sweep_v33

V15_DIR = Path("outputs/realdata_zenodo_14363732_v15_readout")


def test_v33_builds_multiple_splits():
    matrix = load_v15_realdata_matrix_v32(V15_DIR)
    splits = build_culture_splits_v33(matrix, RealDataSweepConfigV33(split_offsets=(0, 1, 2), shuffle_count=1))
    assert len(splits) >= 2
    assert all(s.train_idx and s.test_idx for s in splits)
    assert all(s.overlapping_labels for s in splits)


def test_v33_builds_feature_ablations():
    matrix = load_v15_realdata_matrix_v32(V15_DIR)
    ablations = build_feature_ablations_v33(matrix, RealDataSweepConfigV33())
    ids = {a.ablation_id for a in ablations}
    assert "all_features" in ids
    assert "response_delta_count" in ids
    assert all(a.feature_count > 0 for a in ablations)


def test_v33_compact_run_writes_outputs(tmp_path):
    out = tmp_path / "v33"
    config = RealDataSweepConfigV33(split_offsets=(0, 1), decoders=("centroid_euclidean", "centroid_cosine"), ablations=("response_delta_count", "response_count"), shuffle_count=2, seed=333)
    summary = run_realdata_sweep_v33(V15_DIR, out, config)
    assert summary["status"] == "completed_software_only_replay_sweep"
    assert summary["run_count"] == 8
    assert (out / "paper_table_sweep_results_v33.csv").exists()
    assert (out / "BIOGPU_V33_PAPER_GRADE_SWEEP_REPORT.md").exists()
    assert (out / "biogpu_v33_paper_grade_sweep_result_bundle.zip").exists()


def test_v33_summary_keeps_claim_boundary(tmp_path):
    out = tmp_path / "v33_boundary"
    config = RealDataSweepConfigV33(split_offsets=(0,), decoders=("centroid_euclidean",), ablations=("response_delta_count",), shuffle_count=1)
    summary = run_realdata_sweep_v33(V15_DIR, out, config)
    assert summary["live_output_performed"] is False
    assert summary["gpu_advantage_claimed"] is False
