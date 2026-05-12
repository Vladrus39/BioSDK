import numpy as np
from biogpu.decoding import LinearReadout

def test_decoder_fit_predict():
    X = np.vstack([np.zeros((5,3)), np.ones((5,3))])
    y = np.array([0]*5 + [1]*5)
    dec = LinearReadout().fit(X, y)
    pred = dec.predict(X)
    assert len(pred) == len(y)
