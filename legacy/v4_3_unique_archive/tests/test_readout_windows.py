from biogpu.schemas import SpikeTrain
from biogpu.reading import BasicSpikeFeatureExtractor


def test_readout_bins_add_features():
    st = SpikeTrain(unit_ids=[0, 1, 1], spike_times=[1.0, 5.0, 9.0])
    fv = BasicSpikeFeatureExtractor(num_units=4, window_ms=10.0, readout_bins=2).transform(st)
    # counts + latency + binned counts + summary scalars
    assert len(fv.values) == 4 + 4 + 2 * 4 + 3
    assert fv.metadata["readout_bins"] == 2
