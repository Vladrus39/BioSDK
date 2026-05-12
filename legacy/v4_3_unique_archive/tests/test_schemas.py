import numpy as np
from biogpu.schemas import InputPattern

def test_input_pattern():
    p = InputPattern(id="x", data=np.zeros((4,4)), label=1)
    assert p.id == "x"
    assert p.data.shape == (4,4)
