from biogpu.datasets.orientation import generate_orientation_dataset

def test_orientation_dataset():
    data = generate_orientation_dataset(size=8, samples_per_class=2, noise_levels=[0.0], seed=1)
    assert len(data) == 8
    assert data[0].data.shape == (8,8)
