from biogpu.schemas import StimPattern
from biogpu.substrates import SimulatedMEA

def test_simulated_mea_returns_spikes():
    mea = SimulatedMEA(seed=1, num_electrodes=16, reservoir_units=16)
    mea.connect()
    mea.send_stimulation(StimPattern(substrate_id="sim", channels=[0,1,2], times=[0,0,1], intensities=[1,1,1]))
    spikes = mea.read_spikes(20)
    assert isinstance(spikes.unit_ids, list)
