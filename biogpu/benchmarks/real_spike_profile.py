
from __future__ import annotations
import argparse, json
from typing import Any
import numpy as np
from biogpu.data_ingest.zenodo_mea2100 import ZenodoMEA2100Config, ZenodoMEA2100SpikeTxtAdapter
from biogpu.data_ingest.dandi_nwb import DandiNWBConfig, DandiNWBSpikeAdapter
from biogpu.reading.feature_extractor import BasicSpikeFeatureExtractor
from biogpu.data.versioning import make_run_metadata

def summarize_spiketrain(spikes, window_ms: float) -> dict[str, Any]:
    units=np.asarray(spikes.unit_ids,dtype=int) if spikes.unit_ids else np.asarray([],dtype=int)
    times=np.asarray(spikes.spike_times,dtype=float) if spikes.spike_times else np.asarray([],dtype=float)
    unique=np.unique(units) if units.size else np.asarray([],dtype=int)
    dur=float(window_ms)/1000.0 if window_ms else (float(times.max()-times.min()) if times.size>1 else 0.0)
    return {"spike_count": int(len(times)), "active_units": int(len(unique)), "duration_s": dur, "population_firing_rate_hz": float(len(times)/max(dur,1e-9)), "first_spike_s": float(times.min()) if times.size else None, "last_spike_s": float(times.max()) if times.size else None, "source_metadata": spikes.metadata}

def run_zenodo_profile(root_path: str, window_ms: float=1000.0, spike_glob: str='**/*.txt', time_unit: str='s') -> dict[str, Any]:
    adapter=ZenodoMEA2100SpikeTxtAdapter(ZenodoMEA2100Config(root_path=root_path, spike_glob=spike_glob, time_unit=time_unit)); adapter.connect(); spikes=adapter.read_spikes(window_ms)
    features=BasicSpikeFeatureExtractor(num_units=max(spikes.unit_ids)+1 if spikes.unit_ids else 1).transform(spikes)
    result={"benchmark":"real_spike_profile_zenodo_mea2100", "metadata":make_run_metadata("0.7", {"root_path":root_path,"window_ms":window_ms,"spike_glob":spike_glob}), "health":adapter.health_check(), "metrics":summarize_spiketrain(spikes, window_ms), "features":{"names":features.names,"values":features.values.tolist()}}
    adapter.close(); return result

def run_dandi_profile(nwb_path: str, window_ms: float=1000.0) -> dict[str, Any]:
    adapter=DandiNWBSpikeAdapter(DandiNWBConfig(nwb_path=nwb_path)); adapter.connect(); spikes=adapter.read_spikes(window_ms)
    features=BasicSpikeFeatureExtractor(num_units=max(spikes.unit_ids)+1 if spikes.unit_ids else 1).transform(spikes)
    result={"benchmark":"real_spike_profile_dandi_nwb", "metadata":make_run_metadata("0.7", {"nwb_path":nwb_path,"window_ms":window_ms}), "health":adapter.health_check(), "metrics":summarize_spiketrain(spikes, window_ms), "features":{"names":features.names,"values":features.values.tolist()}}
    adapter.close(); return result

def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='source', required=True)
    z=sub.add_parser('zenodo'); z.add_argument('root_path'); z.add_argument('--window-ms', type=float, default=1000.0); z.add_argument('--glob', default='**/*.txt'); z.add_argument('--time-unit', default='s')
    d=sub.add_parser('dandi'); d.add_argument('nwb_path'); d.add_argument('--window-ms', type=float, default=1000.0)
    a=p.parse_args(argv); result=run_zenodo_profile(a.root_path,a.window_ms,a.glob,a.time_unit) if a.source=='zenodo' else run_dandi_profile(a.nwb_path,a.window_ms)
    print(json.dumps(result,indent=2,ensure_ascii=False)); return 0
if __name__ == '__main__': raise SystemExit(main())
