class SpikeReader:
    def __init__(self, substrate):
        self.substrate = substrate

    def read(self, window_ms=20.0):
        return self.substrate.read_spikes(window_ms=window_ms)
