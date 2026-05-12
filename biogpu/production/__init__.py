"""BioGPU-Core production infrastructure package (v6.0+).

This package houses production-grade implementations that close the
12 production readiness gaps identified in v5.49. Each module upgrades
a local contract proof into a self-contained production service.
"""
from biogpu.production.config_v60 import ProductionConfig, load_production_config
from biogpu.production.bootstrap_v60 import ProductionBootstrap, bootstrap_production
from biogpu.production.foundation_v60 import (
    build_production_foundation,
    write_production_foundation_outputs,
)

__all__ = [
    "ProductionConfig",
    "load_production_config",
    "ProductionBootstrap",
    "bootstrap_production",
    "build_production_foundation",
    "write_production_foundation_outputs",
]
