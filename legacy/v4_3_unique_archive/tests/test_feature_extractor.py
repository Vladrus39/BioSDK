from biogpu.schemas import SpikeTrain
from biogpu.reading import BasicSpikeFeatureExtractor

def test_feature_dimensions():
    st = SpikeTrain(unit_ids=[0,1], spike_times=[1.0, 2.0])
    fv = BasicSpikeFeatureExtractor(num_units=4).transform(st)
    assert len(fv.values) == 4 + 4 + 3
