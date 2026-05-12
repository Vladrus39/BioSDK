from __future__ import annotations
import csv,re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np
from biogpu.schemas import SpikeTrain

@dataclass
class RecordingProfile:
    path:str; date:str; culture:str; plate_id:str; div:int|None; condition:str; spot:int|None
    duration_s:float; sampling_hz:float; electrode_count:int; active_electrodes:int; total_spikes:int
    array_rate_hz:float; mean_active_electrode_rate_hz:float; median_electrode_spikes:float; max_electrode_spikes:int

def read_metadata(recording_dir:str|Path)->dict[str,Any]:
    p=Path(recording_dir)/'metadata'/'meta_data.csv'
    if not p.exists(): return {}
    with p.open('r',encoding='utf-8',errors='ignore',newline='') as f:
        return next(csv.DictReader(f, delimiter='\t'), {})

def parse_electrode_number(path:str|Path)->int:
    m=re.search(r'electrode(\d+)', Path(path).name)
    return int(m.group(1)) if m else 0

def read_sample_num_csv(path:str|Path)->list[int]:
    vals=[]; p=Path(path)
    with p.open('r',encoding='utf-8',errors='ignore',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames and 'sample_num' in reader.fieldnames:
            for row in reader:
                v=(row.get('sample_num') or '').strip()
                if not v: continue
                try: vals.append(int(float(v)))
                except ValueError: pass
        else:
            f.seek(0)
            for line in f:
                line=line.strip()
                if not line or line.lower().startswith('sample'): continue
                try: vals.append(int(float(re.split(r'[,;\s]+', line)[0])))
                except ValueError: pass
    return vals

def recording_dir_to_spiketrain(recording_dir:str|Path)->SpikeTrain:
    rec=Path(recording_dir); meta=read_metadata(rec); hz=float(meta.get('sampling_fr_hz') or 20000.0)
    ids=[]; times=[]
    for f in sorted(rec.glob('electrode*.csv')):
        eid=parse_electrode_number(f)
        for s in read_sample_num_csv(f):
            ids.append(eid); times.append(float(s)/hz)
    order=sorted(range(len(times)), key=lambda i: times[i])
    return SpikeTrain([ids[i] for i in order], [times[i] for i in order], metadata={'source_path':str(rec),'parser':'zenodo_14363732_preprocessed_sample_num_csv','sampling_hz':hz,'metadata':meta})

def discover_recording_dirs(root_path:str|Path)->list[Path]:
    root=Path(root_path)
    return sorted([p for p in root.rglob('*') if p.is_dir() and any(p.glob('electrode*.csv'))])

def parse_recording_identity(recording_dir:str|Path, root_path:str|Path|None=None, metadata: dict[str, Any] | None = None)->dict[str,Any]:
    rec=Path(recording_dir); name=rec.name; culture=rec.parent.name
    date=''
    for part in rec.parts:
        if re.match(r'\d{2}-\d{2}-\d{4}', part): date=part; break
    m=re.search(r'(.+?)_(\d+)DIV', culture)
    plate=m.group(1) if m else culture.split('_')[0]
    div=int(m.group(2)) if m else None
    sm=re.search(r'[Ss]pot(\d+)', name)
    rel=str(rec.relative_to(root_path)) if root_path else str(rec)
    stim_meta = (metadata or {}).get('stimulation', '') if metadata else ''
    condition = 'lightstim' if ('LightStim' in name or str(stim_meta).strip()) else 'baseline'
    return {'path':rel,'date':date,'culture':culture,'plate_id':plate,'div':div,'condition':condition,'spot':int(sm.group(1)) if sm else None}

def _fast_count_sample_rows(path: str | Path) -> int:
    # Fast count for large preprocessed CSVs; header line is excluded.
    with Path(path).open('rb') as f:
        n = sum(1 for _ in f)
    return max(0, n - 1)

def profile_recording_dir(recording_dir:str|Path, root_path:str|Path|None=None)->RecordingProfile:
    rec=Path(recording_dir); meta=read_metadata(rec); ident=parse_recording_identity(rec, root_path, meta)
    hz=float(meta.get('sampling_fr_hz') or 20000.0); dur=float(meta.get('recording_duration_sec') or 0.0)
    counts=[_fast_count_sample_rows(f) for f in sorted(rec.glob('electrode*.csv'))]
    total=int(sum(counts)); active=int(sum(1 for c in counts if c>0))
    return RecordingProfile(**ident,duration_s=dur,sampling_hz=hz,electrode_count=len(counts),active_electrodes=active,total_spikes=total,array_rate_hz=float(total/dur) if dur else 0.0,mean_active_electrode_rate_hz=float(total/(active*dur)) if active and dur else 0.0,median_electrode_spikes=float(np.median(counts)) if counts else 0.0,max_electrode_spikes=int(max(counts)) if counts else 0)

def profile_dataset(root_path:str|Path)->list[RecordingProfile]:
    root=Path(root_path); return [profile_recording_dir(p, root) for p in discover_recording_dirs(root)]

def profiles_to_dicts(profiles:list[RecordingProfile])->list[dict[str,Any]]:
    return [p.__dict__ for p in profiles]
