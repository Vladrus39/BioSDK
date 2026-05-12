"""BioGPU runtime contracts and offline replay runtime.

This package is the point where BioGPU stops being only an analysis notebook and
becomes a software/hardware architecture: the same contracts can be used by a
real MEA/HD-MEA driver, by a safe dry-run adapter, or by a public-data replay
substrate.
"""

from .contracts import (
    BioGPUClaimStage,
    BioGPUJob,
    BioGPUResult,
    BioGPUTrace,
    BioGPUObjective,
    build_biogpu_claim_ladder,
)
from .replay_runtime import RealDataReplayBioGPUSubstrate, write_v18_biogpu_core_outputs

__all__ = [
    "BioGPUClaimStage",
    "BioGPUJob",
    "BioGPUResult",
    "BioGPUTrace",
    "BioGPUObjective",
    "build_biogpu_claim_ladder",
    "RealDataReplayBioGPUSubstrate",
    "write_v18_biogpu_core_outputs",
]
