#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from biogpu.data_ingest.nwb_stimulus_discovery import inspect_nwb_structure, discover_stimulus_tables, write_nwb_discovery_report

def main()->int:
    p=argparse.ArgumentParser(description='Inspect an NWB file for units/stimulus/interval candidates')
    p.add_argument('nwb_path'); p.add_argument('--output',default=None); a=p.parse_args()
    payload={'structure':inspect_nwb_structure(a.nwb_path),'stimulus_table_candidates':[c.__dict__ for c in discover_stimulus_tables(a.nwb_path)]}
    if a.output:
        out=write_nwb_discovery_report(a.nwb_path,a.output); print(json.dumps({'written':str(out),'candidate_count':len(payload['stimulus_table_candidates'])},indent=2))
    else: print(json.dumps(payload,indent=2,ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
