from __future__ import annotations
import argparse, json
from biogpu.analysis.zenodo_pulse_readout import write_readout_outputs
from biogpu.analysis.zenodo_pulse_v17 import write_v17_outputs_from_v15_matrix

def _ints(v: str) -> list[int]: return [int(x.strip()) for x in v.split(',') if x.strip()]
def _strs(v: str) -> list[str]: return [x.strip() for x in v.split(',') if x.strip()]

def main() -> int:
    p = argparse.ArgumentParser(description='Run BioGPU-Core v1.7 from raw preprocessed MEA root or existing v1.5 matrix')
    p.add_argument('input_path')
    p.add_argument('--out', default='outputs/realdata_zenodo_14363732_v17_paper_grade')
    p.add_argument('--from-v15', action='store_true')
    p.add_argument('--v15-temp-out', default='outputs/realdata_zenodo_14363732_v15_readout')
    p.add_argument('--negative-counts', default='1,3,5')
    p.add_argument('--negative-seeds', default='101,202,303')
    p.add_argument('--readouts', default='centroid,logistic_l2,linear_svm')
    p.add_argument('--feature-sets', default='all_features,raw_candidate_counts_only,all_without_rank_zscore,pulse_context_only_negative_control')
    p.add_argument('--label-shuffles', type=int, default=5)
    a = p.parse_args()
    v15_dir = a.input_path
    if not a.from_v15:
        write_readout_outputs(a.input_path, a.v15_temp_out, n_label_shuffles=1, target_label_shuffles=1, candidate_label_shuffles=1)
        v15_dir = a.v15_temp_out
    result = write_v17_outputs_from_v15_matrix(v15_dir, a.out, negative_counts=_ints(a.negative_counts), negative_seeds=_ints(a.negative_seeds), readouts=_strs(a.readouts), feature_set_names=_strs(a.feature_sets), label_shuffles=a.label_shuffles)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
if __name__ == '__main__': raise SystemExit(main())
