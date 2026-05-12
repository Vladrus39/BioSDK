from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from biogpu.runtime.contracts import BioGPUJob
from biogpu.substrates.live_mea_adapter import LiveMEAAdapterConfig, LiveMEASubstrateAdapter
adapter=LiveMEASubstrateAdapter(LiveMEAAdapterConfig(mode='dry_run'))
result=adapter.run_job(BioGPUJob(job_id='livemea_dry_run_001', task='dry_run_probe', input_payload={'target_electrode':1}))
print(result.to_dict())
