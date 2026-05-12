from __future__ import annotations
import argparse, json
from biogpu.analysis.zenodo_pulse_v17 import write_v17_outputs_from_v15_matrix

def _ints(v: str) -> list[int]: return [int(x.strip()) for x in v.split(',') if x.strip()]
def _strs(v: str) -> list[str]: return [x.strip() for x in v.split(',') if x.strip()]

def main() -> int:
    p = argparse.ArgumentParser(description='Run BioGPU-Core v1.7 readout rerun from saved v1.5 pulse feature matrix')
    p.add_argument('v15_out_dir')
    p.add_argument('--out', default='outputs/realdata_zenodo_14363732_v17_paper_grade')
    p.add_argument('--negative-counts', default='1,3,5')
    p.add_argument('--negative-seeds', default='101,202,303')
    p.add_argument('--readouts', default='centroid,logistic_l2,linear_svm')
    p.add_argument('--feature-sets', default='all_features,raw_candidate_counts_only,all_without_rank_zscore,pulse_context_only_negative_control')
    p.add_argument('--label-shuffles', type=int, default=5)
    a = p.parse_args()
    result = write_v17_outputs_from_v15_matrix(a.v15_out_dir, a.out, negative_counts=_ints(a.negative_counts), negative_seeds=_ints(a.negative_seeds), readouts=_strs(a.readouts), feature_set_names=_strs(a.feature_sets), label_shuffles=a.label_shuffles)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
if __name__ == '__main__': raise SystemExit(main())
