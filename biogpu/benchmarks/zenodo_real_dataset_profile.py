from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import numpy as np
from biogpu.data_ingest.zenodo_mea2100_preprocessed import profile_dataset, profiles_to_dicts, recording_dir_to_spiketrain

def run_zenodo_real_dataset_profile(root_path:str, output_dir:str|None=None)->dict[str,Any]:
    rows=profiles_to_dicts(profile_dataset(root_path)); conditions={}; spots=set()
    for r in rows:
        conditions[r['condition']]=conditions.get(r['condition'],0)+1
        if r['spot'] is not None: spots.add(int(r['spot']))
    summary={'benchmark':'zenodo_14363732_real_dataset_profile','root_path':root_path,'recording_count':len(rows),'culture_count':len({r['culture'] for r in rows}),'plate_count':len({r['plate_id'] for r in rows}),'conditions':conditions,'lightstim_spots':sorted(spots),'total_spikes_all_recordings':int(sum(r['total_spikes'] for r in rows)),'median_recording_duration_s':float(np.median([r['duration_s'] for r in rows])) if rows else 0.0,'median_active_electrodes':float(np.median([r['active_electrodes'] for r in rows])) if rows else 0.0,'median_total_spikes_per_recording':float(np.median([r['total_spikes'] for r in rows])) if rows else 0.0,'median_array_rate_hz':float(np.median([r['array_rate_hz'] for r in rows])) if rows else 0.0,'honesty_note':'This is real spike profile evidence. Task claims require real stimulus windows.'}
    result={'summary':summary,'recordings':rows}
    if output_dir:
        out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
        (out/'zenodo_14363732_profile.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return result

def read_one_recording_spiketrain(recording_dir:str):
    return recording_dir_to_spiketrain(recording_dir)
