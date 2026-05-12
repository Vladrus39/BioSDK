from __future__ import annotations
import argparse
from pathlib import Path
from biogpu.runtime.engineering_v19 import write_v19_engineering_outputs

def main():
    p=argparse.ArgumentParser(description='BioGPU-Core v1.9 engineering blueprint')
    p.add_argument('--v15-out', default='outputs/realdata_zenodo_14363732_v15_readout')
    p.add_argument('--out', default='outputs/realdata_zenodo_14363732_v19_engineering')
    p.add_argument('--image', default='')
    p.add_argument('--closed-loop-steps', type=int, default=8)
    p.add_argument('--seed', type=int, default=19)
    a=p.parse_args(); img=Path(a.image) if a.image else None
    print(write_v19_engineering_outputs(a.v15_out, a.out, img, a.closed_loop_steps, a.seed))
if __name__=='__main__': main()
