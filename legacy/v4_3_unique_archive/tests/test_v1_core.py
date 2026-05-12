import numpy as np
from biogpu.reservoir.v1_core import V1Core


def test_v1_core_vector_has_four_orientation_banks():
    core = V1Core()
    img = np.zeros((16, 16), dtype=np.float32)
    img[8, :] = 1.0
    vec = core.transform_vector(img)
    assert vec.shape == (4 * 16 * 16,)
    assert float(vec.sum()) > 0.0


def test_v1_core_dominant_orientation_returns_known_bank():
    core = V1Core()
    img = np.zeros((16, 16), dtype=np.float32)
    img[8, :] = 1.0
    assert core.dominant_orientation(img) in core.ORIENTATIONS
