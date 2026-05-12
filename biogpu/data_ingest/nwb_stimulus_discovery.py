from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
from typing import Any
import json,h5py,numpy as np
@dataclass(frozen=True)
class NWBTableCandidate:
    path:str; kind:str; keys:list[str]; row_count:int|None; reason:str

def _keys(g):
    try: return list(g.keys())
    except Exception: return []
def _shape(o):
    try: return tuple(o.shape)
    except Exception: return None

def inspect_nwb_structure(nwb_path:str|Path,max_depth:int=3,max_items:int=500)->dict[str,Any]:
    p=Path(nwb_path); out={'path':str(p),'exists':p.exists(),'groups':[],'datasets':[]}
    if not p.exists(): return out
    with h5py.File(p,'r') as h5:
        def walk(name,obj):
            if len(out['groups'])+len(out['datasets'])>=max_items: return
            depth=0 if name=='' else name.count('/')+1
            if depth>max_depth: return
            path='/' + name if name else '/'
            if isinstance(obj,h5py.Group): out['groups'].append({'path':path,'keys':_keys(obj)[:30]})
            elif isinstance(obj,h5py.Dataset): out['datasets'].append({'path':path,'shape':_shape(obj),'dtype':str(obj.dtype)})
        h5.visititems(walk)
        out.update({'top_level_keys':list(h5.keys()),'has_units':'units' in h5,'has_intervals':'intervals' in h5,'has_stimulus':'stimulus' in h5,'has_trials':'intervals' in h5 and 'trials' in h5['intervals']})
    return out

def discover_stimulus_tables(nwb_path:str|Path)->list[NWBTableCandidate]:
    p=Path(nwb_path); c=[]
    if not p.exists(): return c
    with h5py.File(p,'r') as h5:
        if 'intervals' in h5:
            for key,g in h5['intervals'].items():
                if isinstance(g,h5py.Group):
                    ks=_keys(g); n=None
                    for k in ('start_time','stop_time','start','stop'):
                        if k in g and isinstance(g[k],h5py.Dataset): n=int(g[k].shape[0]); break
                    bits=[]
                    if any(k in ks for k in ('start_time','stop_time','start','stop')): bits.append('has time boundaries')
                    if any(('label' in k.lower() or 'stim' in k.lower() or 'trial' in k.lower() or 'condition' in k.lower()) for k in ks): bits.append('has label/stim/trial-like columns')
                    c.append(NWBTableCandidate(f'/intervals/{key}','interval_table',ks,n,'; '.join(bits) or 'interval group'))
        if 'stimulus' in h5:
            def scan(name,obj):
                if isinstance(obj,h5py.Group) and _keys(obj): c.append(NWBTableCandidate(f'/stimulus/{name}' if name else '/stimulus','stimulus_group',_keys(obj),None,'stimulus group candidate'))
            h5['stimulus'].visititems(scan)
        if 'trials' in h5 and isinstance(h5['trials'],h5py.Group): c.append(NWBTableCandidate('/trials','trial_table',_keys(h5['trials']),None,'top-level trials group'))
    return c

def candidates_as_dict(candidates:list[NWBTableCandidate])->list[dict[str,Any]]: return [asdict(x) for x in candidates]
def write_nwb_discovery_report(nwb_path:str|Path,output:str|Path)->Path:
    p=Path(output); p.parent.mkdir(parents=True,exist_ok=True); payload={'structure':inspect_nwb_structure(nwb_path),'stimulus_table_candidates':candidates_as_dict(discover_stimulus_tables(nwb_path)),'next_step':'Map a candidate table to stimulus_windows.csv with real start_s,end_s,label.'}; p.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8'); return p

def build_windows_from_simple_intervals(nwb_path:str|Path, interval_path:str, label_column:str|None=None)->list[dict[str,Any]]:
    out=[]
    with h5py.File(nwb_path,'r') as h5:
        key=interval_path.strip('/')
        if key not in h5: raise KeyError(f'Interval path not found: {interval_path}')
        g=h5[key]; sk='start_time' if 'start_time' in g else 'start' if 'start' in g else None; ek='stop_time' if 'stop_time' in g else 'stop' if 'stop' in g else None
        if not sk or not ek: raise ValueError(f'{interval_path} lacks start/stop datasets')
        starts=np.asarray(g[sk][:],dtype=float); stops=np.asarray(g[ek][:],dtype=float); labels=None
        if label_column and label_column in g:
            raw=g[label_column][:]; labels=[x.decode('utf-8') if isinstance(x,bytes) else str(x) for x in raw]
        for i,(s,e) in enumerate(zip(starts,stops)):
            out.append({'start_s':float(s),'end_s':float(e),'label':labels[i] if labels is not None else None,'stimulus_id':f"{interval_path.strip('/').replace('/','_')}_{i}",'split':None,'source_interval_path':interval_path})
    return out
