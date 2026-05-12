import numpy as np
from biogpu.schemas import InputPattern
from biogpu.encoding import SpatialRateEncoder
from biogpu.stimulation import StimulationPlanner, SimulationSafetyLayer

def test_stimulation_plan_valid():
    es = SpatialRateEncoder().encode(InputPattern(id="p", data=np.eye(4)))
    stim = StimulationPlanner().plan(es)
    SimulationSafetyLayer().validate(stim)
    assert len(stim.channels) == len(stim.times) == len(stim.intensities)
