from biogpu.schemas import StimPattern
from biogpu.substrates import RealMEAVendorNeutralAdapter, RealMEAConfig


def test_real_mea_dry_run_contract():
    adapter = RealMEAVendorNeutralAdapter(RealMEAConfig(electrode_count=128))
    adapter.connect()
    adapter.send_stimulation(StimPattern(substrate_id="dry", channels=[1], times=[0.0], intensities=[0.5]))
    spikes = adapter.read_spikes(10)
    health = adapter.health_check()
    assert health["dry_run"] is True
    assert health["capabilities"]["electrode_count"] == 128
    assert spikes.metadata["mode"] == "dry_run"
    adapter.close()
