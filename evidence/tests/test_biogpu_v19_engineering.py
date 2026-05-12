from biogpu.runtime.contracts import BioGPUJob, BioGPUResult, BioGPUTrace
from biogpu.runtime.engineering_v19 import BioGPUClosedLoopReplayRunner, build_benchmark_registry_v19, build_material_plan_v19, build_prototype_plan_v19
from biogpu.substrates.live_mea_adapter import LiveMEAAdapterConfig, LiveMEASubstrateAdapter

class FakeReplaySubstrate:
    def available_targets(self): return [1,2,3]
    def run_job(self, job: BioGPUJob):
        trace=BioGPUTrace(job_id=job.job_id, source='fake', culture='culture_a', recording='rec_a', target_electrode=job.input_payload.get('target_electrode'), response_features=[1.0,0.0,2.0], feature_names=['a','b','c'], metadata={})
        return BioGPUResult(job_id=job.job_id, prediction=trace.target_electrode, confidence=None, metrics={'feature_l2_norm':2.2,'feature_nonzero_fraction':0.67}, trace=trace, metadata={})

def test_material_plan_first_material_is_2d_mea():
    m=build_material_plan_v19()[0]
    assert '2D' in m.biological_material
    assert 'MEA' in m.interface_material
    assert m.readiness=='ready_for_design'

def test_benchmark_registry_has_closed_loop():
    ids={t.task_id for t in build_benchmark_registry_v19()}
    assert 'B0_target_vs_random_electrode' in ids
    assert 'B4_adaptive_closed_loop' in ids

def test_plan_keeps_biogpu_goal():
    p=build_prototype_plan_v19()
    assert 'biological computing accelerator' in p.main_goal
    assert '2D' in p.selected_first_material
    assert len(p.hardware_layers)>=5

def test_live_mea_dry_run_safe():
    a=LiveMEASubstrateAdapter(LiveMEAAdapterConfig(mode='dry_run'))
    r=a.run_job(BioGPUJob(job_id='dry', task='probe', input_payload={'target_electrode':7}))
    assert r.metrics['dry_run'] is True
    assert r.trace.metadata['no_live_stimulation_performed'] is True

def test_closed_loop_runner_scaffold():
    rows=BioGPUClosedLoopReplayRunner(FakeReplaySubstrate(), seed=1).run_demo(3)
    assert len(rows)==3
    assert all(r.decision in {'keep_or_refine_neighborhood','switch_target'} for r in rows)
