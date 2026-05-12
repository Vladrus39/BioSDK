#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from biogpu.data_ingest.zenodo_mea2100 import inspect_spike_txt_folder
from biogpu.data_ingest.public_data_report import write_public_data_status_report

def main()->int:
    p=argparse.ArgumentParser(description='Create BioGPU public-data status report')
    p.add_argument('--zenodo-root',default=None); p.add_argument('--output',default='outputs/reports/public_data_status_v09.md'); a=p.parse_args()
    extra={}
    if a.zenodo_root: extra['zenodo_local_profile']=inspect_spike_txt_folder(a.zenodo_root)
    out=write_public_data_status_report(a.output,extra=extra); print(json.dumps({'written':str(out)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
