from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
ZENODO_RECORD_ID='14363732'; ZENODO_RECORD_URL=f'https://zenodo.org/records/{ZENODO_RECORD_ID}'; ZENODO_API_URL=f'https://zenodo.org/api/records/{ZENODO_RECORD_ID}'
@dataclass(frozen=True)
class ZenodoFileSpec:
    filename:str; size_mb:float; md5:str|None; role:str; recommended_stage:str; direct_url:str; download_by_default:bool=False

def zenodo_14363732_files()->list[ZenodoFileSpec]:
    base=f'https://zenodo.org/records/{ZENODO_RECORD_ID}/files'
    return [
        ZenodoFileSpec('Pre_processed_MEA_data.zip',12.1,'56e4be13c4573252f055b6a1f775f9da','preprocessed spike times in TXT after filtering/spike detection','download first; real spike ingestion/profile',f'{base}/Pre_processed_MEA_data.zip?download=1',True),
        ZenodoFileSpec('final_simulations_paper.zip',86.8,'d80b96f690a0698035d49e221a4d0d2f','NEST simulation spike data from related work','optional comparison to simulated networks',f'{base}/final_simulations_paper.zip?download=1'),
        ZenodoFileSpec('all_simulation_to_produce_final_graphs_spicodyn.zip',144.5,'25e37b9b739bafd33b273e5e229e4f09','data for reproducing figures/simulations','optional later reproducibility work',f'{base}/all_simulation_to_produce_final_graphs_spicodyn.zip?download=1'),
        ZenodoFileSpec('Raw_data_MEA_data.zip',35900.0,'189bf2fc0ce858fd1308d683e1e8c323','raw HDF5 electrophysiological recordings from MEA2100-mini 60-electrode MEA','download only with >40GB free storage',f'{base}/Raw_data_MEA_data.zip?download=1'),
    ]

def zenodo_manifest_dict()->dict[str,Any]:
    return {'record_id':ZENODO_RECORD_ID,'record_url':ZENODO_RECORD_URL,'api_url':ZENODO_API_URL,'title':'MEA recordings dataset','published':'2024-12-10','license':'CC-BY-NC-4.0','hardware':'Multichannel GmbH MEA2100-mini system, 60 electrodes MEA','honesty_note':'Spike times support real spike profiling. Task benchmarks require real stimulus windows/labels.','files':[asdict(f) for f in zenodo_14363732_files()]}

def write_zenodo_manifest(path:str|Path)->Path:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(zenodo_manifest_dict(),indent=2,ensure_ascii=False),encoding='utf-8'); return p

def recommended_downloads(max_mb:float=200.0)->list[dict[str,Any]]:
    return [asdict(f) for f in zenodo_14363732_files() if f.download_by_default and f.size_mb<=max_mb]
