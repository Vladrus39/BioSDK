# Real Signal Pivot Plan — v0.6

## Why pivot

The simulated reservoir is useful for software integration but not yet a source of convincing scientific signal. Continuing to tune it without real hardware or real neural data risks producing infrastructure growth without evidence growth.

## New priorities

### Priority 1 — Evidence quality

Add tools that detect false progress:

- repeated-seed summary statistics;
- regression diagnostics;
- reservoir-vs-shuffled margins;
- reservoir-vs-random margins;
- raw baseline comparison;
- ablation summaries.

### Priority 2 — Hardware readiness

Keep improving the adapter layer:

- vendor-neutral RealMEA contract;
- MaxOne-like dry-run contract;
- NWB/HDF5 export skeleton;
- lab requirements checklist;
- API boundaries.

### Priority 3 — External signal acquisition

Prepare two outreach paths:

- Intel NRC / Loihi 2 proposal;
- MEA laboratory collaboration email.

## Stop criteria for SimulatedMEA tuning

Do not spend more effort tuning SimulatedMEA performance unless at least one of the following is true:

1. a new benchmark exposes a clear online-memory regime where raw/static baselines are weak;
2. repeated seeds show reservoir margin above shuffled/random baselines;
3. the change improves adapter/data/benchmark validity rather than only one accuracy score;
4. it prepares direct translation to Loihi/SNN/MEA.

## Continue criteria

Continue SimulatedMEA only for:

- CLI/API testing;
- data export testing;
- visual report generation;
- repeated-seed evaluation;
- adapter contract testing;
- benchmark reproducibility.
