
from __future__ import annotations

import csv, json, time, zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.integration.realdata_replay_v32 import load_v15_realdata_matrix_v32, RealDataMatrixV32
from biogpu.metrics.energy_model_v29 import EnergyRunInputV29, PowerComponentV29, estimate_energy_v29
from biogpu.metrics.latency_model_v29 import LatencyComponentsV29, estimate_latency_v29
from biogpu.runtime.session_manager_v24 import BioGPUAuditLog, artifact_ref, build_v24_manifest, validate_manifest

SAFETY_BOUNDARY_V33 = [
    'offline public-data replay only',
    'no live stimulation settings emitted',
    'no wet-lab protocol',
    'no vendor pinout or wiring procedure',
    'no GPU advantage claim',
]

@dataclass(frozen=True)
class RealDataSweepConfigV33:
    version: str = 'v3.3'
    benchmark_id: str = 'B1_spot_localization:paper_grade_realdata_sweep'
    split_offsets: tuple[int, ...] = (0, 1, 2, 3, 4, 5)
    culture_stride: int = 3
    heldout_culture_count: int = 5
    decoders: tuple[str, ...] = ('centroid_euclidean', 'centroid_cosine', 'diag_gaussian')
    ablations: tuple[str, ...] = ('all_features', 'response_delta_count', 'response_count', 'pre_response_count', 'exact_features')
    shuffle_count: int = 12
    seed: int = 33
    task_count_for_energy: int = 1000
    run_duration_s_for_energy: float = 60.0
    operator_note: str = 'v3.3 compact paper-grade real-data sweep on Zenodo pulse-window features'
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class CultureSplitV33:
    split_id: str
    offset: int
    train_idx: list[int]
    test_idx: list[int]
    test_cultures: list[str]
    overlapping_labels: list[int]
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class FeatureAblationV33:
    ablation_id: str
    feature_indices: list[int]
    feature_count: int
    description: str
    def to_dict(self): return asdict(self)


def _json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def _csv(path, rows):
    path = Path(path)
    if not rows:
        path.write_text('', encoding='utf-8'); return
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)


def build_culture_splits_v33(matrix: RealDataMatrixV32, config: RealDataSweepConfigV33):
    matrix.validate()
    cultures = sorted(set(map(str, matrix.cultures)))
    out=[]; stride=max(1, int(config.culture_stride)); held=max(1, int(config.heldout_culture_count))
    for offset in config.split_offsets:
        test=[]
        for j in range(len(cultures)*stride):
            c = cultures[(int(offset)+j*stride) % len(cultures)]
            if c not in test: test.append(c)
            if len(test) >= held: break
        is_test = np.isin(matrix.cultures.astype(str), np.asarray(test, dtype=str))
        train_mask, test_mask = ~is_test, is_test
        overlapping = sorted(set(map(int, matrix.y[train_mask])) & set(map(int, matrix.y[test_mask])))
        if not overlapping: continue
        label_mask = np.isin(matrix.y, np.asarray(overlapping, dtype=int))
        train_idx = np.where(train_mask & label_mask)[0].astype(int).tolist()
        test_idx = np.where(test_mask & label_mask)[0].astype(int).tolist()
        if train_idx and test_idx:
            out.append(CultureSplitV33(f'culture_holdout_offset_{int(offset)}', int(offset), train_idx, test_idx, test, [int(x) for x in overlapping]))
    if not out: raise ValueError('No valid v3.3 culture-heldout splits')
    return out


def build_feature_ablations_v33(matrix: RealDataMatrixV32, config: RealDataSweepConfigV33):
    names=list(map(str, matrix.feature_names))
    specs = {
        'all_features': (None, 'All v1.5 pulse-window features'),
        'response_delta_count': ('response_delta_count', 'Post-minus-pre response delta count per electrode'),
        'response_count': ('response_count', 'Post-response count per electrode'),
        'pre_response_count': ('pre_response_count', 'Pre-window baseline response count per electrode'),
        'exact_features': ('exact_', 'Exact-window derived features from v1.5 feature builder'),
    }
    out=[]
    for aid in config.ablations:
        if aid not in specs: continue
        prefix, desc = specs[aid]
        idx = list(range(len(names))) if prefix is None else [i for i,n in enumerate(names) if n.startswith(prefix)]
        if idx: out.append(FeatureAblationV33(aid, idx, len(idx), desc))
    if not out: raise ValueError('No valid v3.3 feature ablations')
    return out


def _standardize(Xtr, Xte):
    mu=Xtr.mean(axis=0); sd=Xtr.std(axis=0); sd=np.where(sd<1e-9, 1.0, sd)
    return (Xtr-mu)/sd, (Xte-mu)/sd


def _centroids(X, y, labels):
    return np.vstack([X[y==int(l)].mean(axis=0) for l in labels])


def _predict(decoder, Xte, Xtr, ytr, labels):
    labels_arr=np.asarray(labels, dtype=int)
    c=_centroids(Xtr, ytr, labels)
    if decoder == 'centroid_euclidean':
        d=((Xte[:,None,:]-c[None,:,:])**2).sum(axis=2)
        return labels_arr[np.argmin(d, axis=1)]
    if decoder == 'centroid_cosine':
        cn=c/(np.linalg.norm(c, axis=1, keepdims=True)+1e-12)
        xn=Xte/(np.linalg.norm(Xte, axis=1, keepdims=True)+1e-12)
        return labels_arr[np.argmax(xn @ cn.T, axis=1)]
    if decoder == 'diag_gaussian':
        scores=[]
        for l in labels:
            rows=Xtr[ytr==int(l)]; mu=rows.mean(axis=0); var=rows.var(axis=0)+1e-2
            scores.append((-0.5*(((Xte-mu)**2)/var + np.log(var)).sum(axis=1)))
        return labels_arr[np.argmax(np.vstack(scores).T, axis=1)]
    if decoder in {'logistic_l2', 'logistic_l2_v27'}:
        from sklearn.linear_model import LogisticRegression
        clf=LogisticRegression(C=1.0, solver='lbfgs', max_iter=2000, random_state=33)
        clf.fit(Xtr, ytr)
        return clf.predict(Xte).astype(int)
    if decoder in {'linear_svm', 'linear_svm_v27'}:
        from sklearn.svm import LinearSVC
        clf=LinearSVC(C=1.0, max_iter=5000, random_state=33, dual='auto')
        clf.fit(Xtr, ytr)
        return clf.predict(Xte).astype(int)
    raise ValueError(f'unknown decoder: {decoder}')


def _balanced(y, pred, labels):
    vals=[]
    for l in labels:
        m=y==int(l)
        if np.any(m): vals.append(float(np.mean(pred[m]==int(l))))
    return float(np.mean(vals)) if vals else 0.0


def evaluate_one_v33(matrix, split, ablation, decoder, config, rng):
    train=np.asarray(split.train_idx, dtype=int); test=np.asarray(split.test_idx, dtype=int)
    feat=np.asarray(ablation.feature_indices, dtype=int); labels=[int(x) for x in split.overlapping_labels]
    Xtr_raw=matrix.X[train][:,feat]; Xte_raw=matrix.X[test][:,feat]
    ytr=matrix.y[train].astype(int); yte=matrix.y[test].astype(int)
    Xtr,Xte=_standardize(Xtr_raw, Xte_raw)
    pred=_predict(decoder, Xte, Xtr, ytr, labels)
    acc=float(np.mean(pred==yte)); bal=_balanced(yte, pred, labels); chance=float(1/len(labels))
    shuf_acc=[]; shuf_rows=[]
    for i in range(int(config.shuffle_count)):
        ys=ytr.copy(); rng.shuffle(ys)
        ps=_predict(decoder, Xte, Xtr, ys, labels)
        a=float(np.mean(ps==yte)); shuf_acc.append(a)
        shuf_rows.append({'split_id':split.split_id,'decoder_id':decoder,'ablation_id':ablation.ablation_id,'shuffle_index':i,'accuracy':a})
    sm=float(np.mean(shuf_acc)) if shuf_acc else 0.0; ss=float(np.std(shuf_acc)) if shuf_acc else 0.0; sx=float(np.max(shuf_acc)) if shuf_acc else 0.0
    p=float((sum(1 for a in shuf_acc if a>=acc)+1)/(len(shuf_acc)+1)) if shuf_acc else 1.0
    row={'split_id':split.split_id,'decoder_id':decoder,'ablation_id':ablation.ablation_id,'n_train':len(train),'n_test':len(test),'n_labels':len(labels),'n_features':len(feat),'accuracy':acc,'balanced_accuracy':bal,'chance_approx':chance,'shuffle_mean_accuracy':sm,'shuffle_std_accuracy':ss,'shuffle_max_accuracy':sx,'improvement_vs_shuffle_mean':acc-sm,'empirical_p_value_shuffled_ge_real':p,'status':'ok'}
    return row, shuf_rows


def _group(rows, key):
    out=[]
    for val in sorted(set(str(r[key]) for r in rows)):
        xs=[r for r in rows if str(r[key])==val]
        acc=[float(r['accuracy']) for r in xs]; bal=[float(r['balanced_accuracy']) for r in xs]; imp=[float(r['improvement_vs_shuffle_mean']) for r in xs]
        out.append({key:val,'n_runs':len(xs),'mean_accuracy':float(np.mean(acc)),'std_accuracy':float(np.std(acc)),'mean_balanced_accuracy':float(np.mean(bal)),'mean_improvement_vs_shuffle':float(np.mean(imp)),'best_accuracy':float(np.max(acc))})
    return out


def _best_by(rows, key):
    out=[]
    for val in sorted(set(str(r[key]) for r in rows)):
        xs=[r for r in rows if str(r[key])==val]
        best=max(xs, key=lambda r:(float(r['accuracy']), float(r['balanced_accuracy']), float(r['improvement_vs_shuffle_mean'])))
        out.append({key:val, **best})
    return out


def _energy_latency(config, best):
    energy=estimate_energy_v29(EnergyRunInputV29(task_count=config.task_count_for_energy, run_duration_s=config.run_duration_s_for_energy, components=(PowerComponentV29('host_replay_pc',65.0,'offline paper sweep runtime','placeholder'), PowerComponentV29('storage_logging_share',5.0,'audit/result bundle storage','placeholder')), notes='v3.3 replay energy accounting only; live substrate energy is not included.'))
    latency=estimate_latency_v29(LatencyComponentsV29(encode_ms=0.5, substrate_io_ms=0.0, biological_response_ms=0.0, acquisition_ms=0.0, feature_extraction_ms=1.0, readout_ms=3.0, controller_update_ms=0.0, notes='v3.3 offline matrix sweep latency placeholder; not a live BioGPU latency measurement.'))
    return {'version':'v3.3','scientific_boundary':'Replay-only energy/latency accounting; does not prove live BioGPU or GPU advantage.','best_accuracy':best['accuracy'],'best_decoder':best['decoder_id'],'best_ablation':best['ablation_id'],'energy':energy.to_dict(),'latency':latency.to_dict()}


def _plots(out, rows):
    made=[]
    try:
        import matplotlib.pyplot as plt
        decs=sorted(set(r['decoder_id'] for r in rows)); data=[[float(r['accuracy']) for r in rows if r['decoder_id']==d] for d in decs]
        plt.figure(figsize=(8,4.5)); plt.boxplot(data, labels=decs, showmeans=True); plt.ylabel('Accuracy'); plt.title('BioGPU v3.3 accuracy by decoder'); plt.xticks(rotation=20, ha='right'); plt.tight_layout(); p=Path(out)/'v33_accuracy_by_decoder.png'; plt.savefig(p,dpi=150); plt.close(); made.append(p.name)
        abls=sorted(set(r['ablation_id'] for r in rows)); means=[float(np.mean([float(r['accuracy']) for r in rows if r['ablation_id']==a])) for a in abls]
        plt.figure(figsize=(8,4.5)); plt.bar(range(len(abls)), means); plt.xticks(range(len(abls)), abls, rotation=25, ha='right'); plt.ylabel('Mean accuracy'); plt.title('BioGPU v3.3 mean accuracy by feature ablation'); plt.tight_layout(); p=Path(out)/'v33_mean_accuracy_by_ablation.png'; plt.savefig(p,dpi=150); plt.close(); made.append(p.name)
    except Exception:
        pass
    return made


def _report(profile, summary):
    b=summary['best_run']
    dec='\n'.join([f"- `{r['decoder_id']}`: mean acc `{r['mean_accuracy']:.4f}`, best `{r['best_accuracy']:.4f}`" for r in summary['aggregate_by_decoder']])
    abl='\n'.join([f"- `{r['ablation_id']}`: mean acc `{r['mean_accuracy']:.4f}`, best `{r['best_accuracy']:.4f}`" for r in summary['aggregate_by_ablation']])
    return f"""# BioGPU-Core v3.3 Paper-grade Real-data E2E Sweep

## Status

`COMPLETED_SOFTWARE_ONLY_REPLAY_SWEEP`

## Dataset

- Rows / pulse windows: `{profile['rows']}`
- Features: `{profile['features']}`
- Cultures: `{profile['cultures']}`
- Target classes: `{profile['target_classes']}`
- Conditions: `{', '.join(profile['conditions'])}`

## Best compact-run result

- Split: `{b['split_id']}`
- Decoder: `{b['decoder_id']}`
- Ablation: `{b['ablation_id']}`
- Accuracy: `{float(b['accuracy']):.6f}`
- Balanced accuracy: `{float(b['balanced_accuracy']):.6f}`
- Chance approx: `{float(b['chance_approx']):.6f}`
- Shuffled mean accuracy: `{float(b['shuffle_mean_accuracy']):.6f}`
- Improvement vs shuffle mean: `{float(b['improvement_vs_shuffle_mean']):.6f}`
- Empirical p-value, shuffled >= real: `{float(b['empirical_p_value_shuffled_ge_real']):.6f}`

## Aggregate by decoder

{dec}

## Aggregate by feature ablation

{abl}

## Interpretation

v3.3 upgrades v3.2 from one fixed replay run to a compact paper-grade sweep. It remains intentionally small enough for this environment, but produces the tables and result bundle needed to move the larger study to a power PC.

This is software-only real-data replay evidence, not proof of a live BioGPU prototype and not proof of GPU advantage.

## Safety and scope boundary

{chr(10).join('- '+x for x in SAFETY_BOUNDARY_V33)}

## Heavy-PC backlog

{chr(10).join('- '+x for x in summary['heavy_pc_backlog'])}
"""


def run_realdata_sweep_v33(v15_dir, out_dir, config=None):
    config=config or RealDataSweepConfigV33(); out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    started=time.perf_counter(); audit=BioGPUAuditLog()
    manifest=build_v24_manifest(run_mode='replay', benchmark_ids=['B1_spot_localization','B5_energy_latency_comparison'], hardware_profile='software_only_v33_realdata_sweep', operator_note=config.operator_note)
    object.__setattr__(manifest, 'version', 'v3.3'); manifest.config['v33_realdata_sweep']=config.to_dict(); validation_errors=validate_manifest(manifest)
    audit.add('manifest_created','ok', validation_errors=validation_errors)
    matrix=load_v15_realdata_matrix_v32(v15_dir); profile=matrix.profile(); audit.add('matrix_loaded','ok', rows=profile['rows'], features=profile['features'])
    splits=build_culture_splits_v33(matrix,config); abls=build_feature_ablations_v33(matrix,config); audit.add('sweep_design_created','ok', split_count=len(splits), ablation_count=len(abls), decoder_count=len(config.decoders))
    rng=np.random.default_rng(config.seed); rows=[]; shuf=[]; errors=[]
    for s in splits:
        for a in abls:
            for d in config.decoders:
                try:
                    r, sr=evaluate_one_v33(matrix,s,a,d,config,rng); rows.append(r); shuf.extend(sr)
                except Exception as e:
                    errors.append({'split_id':s.split_id,'ablation_id':a.ablation_id,'decoder_id':d,'error':str(e)})
    if not rows: raise RuntimeError(f'No successful v3.3 runs: {errors[:3]}')
    best=max(rows, key=lambda r:(float(r['accuracy']), float(r['balanced_accuracy']), float(r['improvement_vs_shuffle_mean'])))
    agg_dec=_group(rows,'decoder_id'); agg_abl=_group(rows,'ablation_id'); best_dec=_best_by(rows,'decoder_id'); best_abl=_best_by(rows,'ablation_id')
    backlog=['Increase shuffled-label controls from compact 12/run to 100-1000/run.','Add nested culture-heldout hyperparameter selection for regularized linear models.','Run full feature-set stability analysis over all cultures and target labels.','Add bootstrap confidence intervals for accuracy and balanced accuracy.','Compare centroid/diagonal models with logistic regression, linear SVM and calibrated readouts.','Repeat with raw HDF5/TTL pulse windows if available.']
    summary={'version':'v3.3','status':'completed_software_only_replay_sweep','dataset_rows':profile['rows'],'dataset_features':profile['features'],'cultures':profile['cultures'],'target_classes':profile['target_classes'],'run_count':len(rows),'best_run':best,'best_by_decoder':best_dec,'best_by_ablation':best_abl,'aggregate_by_decoder':agg_dec,'aggregate_by_ablation':agg_abl,'safety_boundary':SAFETY_BOUNDARY_V33,'heavy_pc_backlog':backlog,'errors':errors}
    elapsed=time.perf_counter()-started; audit.add('sweep_completed','ok', run_count=len(rows), error_count=len(errors), elapsed_s=elapsed, best_accuracy=best['accuracy'])
    _json(out/'run_manifest_v33.json', manifest.to_dict()); _json(out/'dataset_profile_v33.json', profile); _json(out/'sweep_config_v33.json', config.to_dict()); _json(out/'split_catalog_v33.json', [s.to_dict() for s in splits]); _json(out/'feature_ablation_catalog_v33.json', [a.to_dict() for a in abls]); _json(out/'sweep_summary_v33.json', summary); _json(out/'sweep_errors_v33.json', errors); _json(out/'energy_latency_report_v33.json', _energy_latency(config,best))
    _csv(out/'paper_table_sweep_results_v33.csv', rows); _csv(out/'paper_table_shuffle_controls_v33.csv', shuf); _csv(out/'paper_table_aggregate_by_decoder_v33.csv', agg_dec); _csv(out/'paper_table_aggregate_by_ablation_v33.csv', agg_abl); _csv(out/'paper_table_best_by_decoder_v33.csv', best_dec); _csv(out/'paper_table_best_by_ablation_v33.csv', best_abl); _csv(out/'paper_table_split_catalog_v33.csv', [s.to_dict() | {'train_count':len(s.train_idx),'test_count':len(s.test_idx)} for s in splits]); _csv(out/'paper_table_feature_ablations_v33.csv', [a.to_dict() for a in abls])
    (out/'BIOGPU_V33_PAPER_GRADE_SWEEP_REPORT.md').write_text(_report(profile,summary), encoding='utf-8'); (out/'POWER_PC_BACKLOG_V33.md').write_text('# BioGPU v3.3 Heavy-PC Backlog\n\n'+'\n'.join('- '+x for x in backlog)+'\n', encoding='utf-8')
    plot_files=_plots(out,rows); audit.add('plots_created','ok', plot_files=plot_files); audit.write_jsonl(out/'audit_log_v33.jsonl')
    artifacts=[artifact_ref(p,out,'v33_output') for p in sorted(out.iterdir()) if p.is_file()]
    session={'version':'v3.3','session_id':manifest.session_id,'status':'completed','validation_errors':validation_errors,'artifact_count':len(artifacts),'artifacts':[a.to_dict() for a in artifacts],'live_output_performed':False,'gpu_advantage_claimed':False,'elapsed_s':elapsed}
    _json(out/'session_summary_v33.json', session)
    bundle=out/'biogpu_v33_paper_grade_sweep_result_bundle.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.iterdir()):
            if p.is_file() and p.name != bundle.name: zf.write(p, arcname=p.name)
    session['result_bundle']=bundle.name; _json(out/'session_summary_v33.json', session)
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.iterdir()):
            if p.is_file() and p.name != bundle.name: zf.write(p, arcname=p.name)
    return {'version':'v3.3','status':summary['status'],'run_count':summary['run_count'],'best_accuracy':float(best['accuracy']),'best_balanced_accuracy':float(best['balanced_accuracy']),'best_decoder':best['decoder_id'],'best_ablation':best['ablation_id'],'best_split':best['split_id'],'best_shuffle_mean_accuracy':float(best['shuffle_mean_accuracy']),'best_improvement_vs_shuffle_mean':float(best['improvement_vs_shuffle_mean']),'validation_errors':validation_errors,'elapsed_s':elapsed,'result_bundle':str(bundle),'live_output_performed':False,'gpu_advantage_claimed':False}
