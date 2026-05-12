#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.request
from pathlib import Path
from biogpu.data_ingest.zenodo_manifest import zenodo_manifest_dict, zenodo_14363732_files

def md5_file(path:Path,chunk_size:int=1024*1024)->str:
    h=hashlib.md5()
    with path.open('rb') as f:
        while True:
            b=f.read(chunk_size)
            if not b: break
            h.update(b)
    return h.hexdigest()
def download(url:str,dest:Path)->None:
    dest.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(url,timeout=60) as r, dest.open('wb') as out:
        while True:
            b=r.read(1024*1024)
            if not b: break
            out.write(b)
def main()->int:
    p=argparse.ArgumentParser(description='Download selected files from Zenodo record 14363732')
    p.add_argument('--out',default='data/zenodo_14363732'); p.add_argument('--manifest',action='store_true'); p.add_argument('--file',action='append',default=[]); p.add_argument('--all-small',action='store_true'); p.add_argument('--max-mb',type=float,default=200.0); p.add_argument('--verify-md5',action='store_true')
    a=p.parse_args()
    if a.manifest: print(json.dumps(zenodo_manifest_dict(),indent=2,ensure_ascii=False)); return 0
    selected=set(a.file or ['Pre_processed_MEA_data.zip']); out=Path(a.out); downloads=[]
    for spec in zenodo_14363732_files():
        if a.all_small and spec.size_mb<=a.max_mb: downloads.append(spec)
        elif spec.filename in selected: downloads.append(spec)
    if not downloads: raise SystemExit('No files selected for download')
    for spec in downloads:
        dest=out/spec.filename; print(f'Downloading {spec.filename} ({spec.size_mb} MB) -> {dest}')
        download(spec.direct_url,dest)
        if a.verify_md5 and spec.md5:
            got=md5_file(dest)
            if got!=spec.md5: raise SystemExit(f'MD5 mismatch for {dest}: expected {spec.md5}, got {got}')
            print(f'MD5 OK: {spec.filename}')
    return 0
if __name__=='__main__': raise SystemExit(main())
