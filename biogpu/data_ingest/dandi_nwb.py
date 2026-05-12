
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import h5py, numpy as np
from biogpu.schemas import SpikeTrain, StimPattern
from biogpu.substrates.base import ComputeSubstrateAdapter

@dataclass
class DandiNWBConfig:
    nwb_path: str
    window_start_s: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

def inspect_nwb_units(nwb_path: str | Path) -> dict[str, Any]:
    path=Path(nwb_path)
    if not path.exists(): return {"path": str(path), "exists": False}
    info={"path": str(path), "exists": True, "has_units": False}
    with h5py.File(path,'r') as h5:
        info['top_level_keys']=list(h5.keys())[:20]
        if 'units' in h5:
            units=h5['units']; info['has_units']=True; info['unit_keys']=list(units.keys())
            if 'spike_times' in units: info['spike_times_count']=int(units['spike_times'].shape[0])
            if 'spike_times_index' in units: info['unit_count_from_index']=int(units['spike_times_index'].shape[0])
    return info

def read_nwb_units_as_spiketrain(nwb_path: str | Path, window_start_s: float=0.0, window_ms: float | None=None) -> SpikeTrain:
    path=Path(nwb_path); unit_ids=[]; spike_times_out=[]
    with h5py.File(path,'r') as h5:
        if 'units' not in h5 or 'spike_times' not in h5['units'] or 'spike_times_index' not in h5['units']:
            raise ValueError('NWB file does not expose /units/spike_times and /units/spike_times_index')
        spike_times=np.asarray(h5['units/spike_times'][:], dtype=float)
        spike_index=np.asarray(h5['units/spike_times_index'][:], dtype=int)
        start_i=0; start_s=float(window_start_s); end_s=start_s+float(window_ms)/1000.0 if window_ms else None
        for unit_id, stop_i in enumerate(spike_index):
            for t in spike_times[start_i:stop_i]:
                if end_s is None or (start_s <= float(t) <= end_s):
                    unit_ids.append(int(unit_id)); spike_times_out.append(float(t))
            start_i=stop_i
    return SpikeTrain(unit_ids, spike_times_out, metadata={"source_path": str(path), "parser": "dandi_nwb_units_h5py", "time_unit_out": "s"})

class DandiNWBSpikeAdapter(ComputeSubstrateAdapter):
    def __init__(self, config: DandiNWBConfig): self.config=config; self._connected=False
    def connect(self) -> None:
        path=Path(self.config.nwb_path)
        if not path.exists(): raise FileNotFoundError(f"NWB file does not exist: {path}")
        info=inspect_nwb_units(path)
        if not info.get('has_units'): raise ValueError('NWB file has no /units table; choose an ecephys NWB file with spike units')
        self._connected=True
    def configure(self, config: dict[str, Any]) -> None:
        for k,v in config.items():
            if hasattr(self.config,k): setattr(self.config,k,v)
    def send_stimulation(self, pattern: StimPattern) -> None: self._last_stim_pattern=pattern
    def read_spikes(self, window_ms: float) -> SpikeTrain:
        if not self._connected: self.connect()
        return read_nwb_units_as_spiketrain(self.config.nwb_path, self.config.window_start_s, window_ms)
    def read_raw(self, window_ms: float): raise NotImplementedError('Raw acquisition mapping is dataset-specific')
    def health_check(self) -> dict[str, Any]: return {"adapter": "DandiNWBSpikeAdapter", "mode": "offline_public_nwb", "connected": self._connected, **inspect_nwb_units(self.config.nwb_path)}
    def close(self) -> None: self._connected=False
