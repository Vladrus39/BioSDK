from biogpu.datasets.delayed_match import generate_delayed_match_dataset


def test_delayed_match_dataset_has_sequences_and_binary_labels():
    data = generate_delayed_match_dataset(size=8, samples_per_class=4, delay_frames=1, seed=1)
    assert len(data) == 8
    assert data[0].data.ndim == 3
    assert set(p.label for p in data) == {0, 1}
