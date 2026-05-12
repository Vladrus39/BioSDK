from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
from typing import Any
import json
@dataclass(frozen=True)
class BRC2602Contract:
    spike_source:str; stimulus_table:str; electrode_map:str|None=None; train_test_split:str|None=None; response_feature_matrix:str|None=None; notes:str='Requires real HD-MEA stimulation/readout data and labels.'
def minimal_brc2602_contract()->dict[str,Any]:
    return asdict(BRC2602Contract('path/to/spikes_or_nwb_or_hdf5','path/to/stimulus_windows.csv','path/to/electrode_map.csv','path/to/splits.csv','optional/path/to/paper_features.npy'))
def write_brc2602_contract(path:str|Path)->Path:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(minimal_brc2602_contract(),indent=2,ensure_ascii=False),encoding='utf-8'); return p
