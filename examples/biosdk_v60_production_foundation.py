"""Minimal SDK example for v6.0 Production Foundation."""
from biogpu.production.config_v60 import ProductionConfig
from biogpu.production.bootstrap_v60 import bootstrap_production
from biogpu.production.foundation_v60 import build_production_foundation


def main():
    print("BioGPU-Core v6.0 Production Foundation - SDK Example")
    print()

    # 1. Load config
    config = ProductionConfig()
    print(f"Config loaded: v{config.config_version}, env={config.environment}")

    # 2. Bootstrap
    result = bootstrap_production(config, ".")
    print(f"Bootstrap: success={result.success}, checks={len(result.checks)}, errors={len(result.errors)}")
    for c in result.checks:
        print(f"  [{c['check']}] passed={c['passed']}")

    # 3. Foundation audit
    audit = build_production_foundation(".")
    print(f"Foundation: open_gaps={audit['open_gap_count']}, ready={audit['production_ready']}")
    print(f"BiC OS locked: {audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()
