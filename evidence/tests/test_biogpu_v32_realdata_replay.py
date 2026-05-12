from __future__ import annotations
import numpy as np
from pathlib import Path
from biogpu.integration.realdata_replay_v32 import (
    RealDataReplayConfigV32,
    build_fixed_culture_split_v32,
    evaluate_realdata_centroid_v32,
    load_v15_realdata_matrix_v32,
    run_realdata_replay_v32,
)


def _make_fixture_v15(tmp_path: Path) -> Path:
    v15 = tmp_path / "v15"
    v15.mkdir()
    rng = np.random.default_rng(123)
    labels = []
    cultures = []
    rows = []
    conds = []
    recs = []
    pulses = []
    # Three labels appear in both train and test cultures.
    culture_names = ["c0", "c1", "c2", "c3", "c4", "c5"]
    label_ids = [10, 20, 30]
    for ci, culture in enumerate(culture_names):
        for lab in label_ids:
            center = np.zeros(6)
            center[label_ids.index(lab)] = 5.0
            for j in range(6):
                rows.append(center + rng.normal(0, 0.05, size=6))
                labels.append(lab)
                cultures.append(culture)
                conds.append("lightstim")
                recs.append(f"rec_{culture}_{lab}")
                pulses.append(j)
    np.savez(
        v15 / "pulse_feature_matrix.npz",
        X=np.asarray(rows, dtype=np.float32),
        target_id=np.asarray(labels, dtype=int),
        culture=np.asarray(cultures, dtype=object),
        condition=np.asarray(conds, dtype=object),
        recording_path=np.asarray(recs, dtype=object),
        pulse_index=np.asarray(pulses, dtype=int),
        feature_names=np.asarray([f"f{i}" for i in range(6)], dtype=object),
    )
    return v15


def test_load_and_profile_fixture(tmp_path):
    v15 = _make_fixture_v15(tmp_path)
    matrix = load_v15_realdata_matrix_v32(v15)
    profile = matrix.profile()
    assert profile["rows"] == 108
    assert profile["features"] == 6
    assert profile["cultures"] == 6


def test_fixed_split_has_overlap(tmp_path):
    v15 = _make_fixture_v15(tmp_path)
    matrix = load_v15_realdata_matrix_v32(v15)
    split = build_fixed_culture_split_v32(matrix, RealDataReplayConfigV32(heldout_culture_count=2, culture_stride=2))
    assert split.train_idx
    assert split.test_idx
    assert split.overlapping_labels == [10, 20, 30]


def test_centroid_beats_chance_on_fixture(tmp_path):
    v15 = _make_fixture_v15(tmp_path)
    matrix = load_v15_realdata_matrix_v32(v15)
    config = RealDataReplayConfigV32(heldout_culture_count=2, culture_stride=2, shuffle_count=3)
    split = build_fixed_culture_split_v32(matrix, config)
    result, shuffles = evaluate_realdata_centroid_v32(matrix, split, config)
    assert result.accuracy > 0.95
    assert result.chance_approx == 1/3
    assert len(shuffles) == 3


def test_run_writes_result_bundle(tmp_path):
    v15 = _make_fixture_v15(tmp_path)
    out = tmp_path / "out"
    summary = run_realdata_replay_v32(v15, out, RealDataReplayConfigV32(heldout_culture_count=2, culture_stride=2, shuffle_count=2))
    assert summary["status"] == "completed_software_only_replay"
    assert (out / "biogpu_v32_realdata_replay_result_bundle.zip").exists()
    assert (out / "BIOGPU_V32_REALDATA_REPLAY_REPORT.md").exists()
