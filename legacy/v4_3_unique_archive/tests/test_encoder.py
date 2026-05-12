import numpy as np
from biogpu.schemas import InputPattern
from biogpu.encoding import SpatialRateEncoder

def test_encoder_emits_events():
    p = InputPattern(id="p", data=np.eye(4), label=0)
    enc = SpatialRateEncoder(max_events_per_pixel=2)
    es = enc.encode(p)
    assert len(es.events) > 0
    assert es.events[0].channel_id >= 0
