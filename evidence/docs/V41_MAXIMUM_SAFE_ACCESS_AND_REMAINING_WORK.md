# BioGPU-Core v4.1 — Maximum Safe Access + Remaining Work Audit

## Decision

v4.1 corrects the beta-access strategy.

Early serious testers should receive **maximum safe software access**, not a crippled demo. They should be able to install the SDK, run Docker/on-prem, use replay benchmarks, upload/import their own data, run lineage-strict splits, run safe readouts, use result bundles, inspect audit logs, test BioLLM tool mode, and validate read-only/mock external API adapters.

The hard boundary is not "small demo vs paid access". The hard boundary is:

```text
safe software/data/API-read functionality: available to serious early testers
live biological/lab actuation: blocked until lab/vendor/protocol approval
```

## Commercial interpretation

The first external testers should see the real value of the SDK:

```text
Developer Evaluation: useful but quota-limited
Research Pilot: maximum safe software access
Enterprise Read-Only: paid production-grade analysis
Enterprise Live Shadow: premium read-only live stream integration
Lab-Approved Closed Loop Add-on: highest-value controlled live module
```

## What remains in this environment

Still possible here before moving fully to power-PC/API/lab:

```text
v4.2 — Dataset registry + import skeleton
v4.3 — Hosted server scaffold + job model
v4.4 — Private beta docs + sample manifests
v4.5 — Security/data handling + enterprise pilot pack
```

## What must move elsewhere

```text
Power PC/server:
- full_shuffle_1000
- extended_methods_5000
- raw HDF5/TTL parsing
- measured energy/latency

External API/partner access:
- FinalSpark/vendor credentials
- real read-only API validation
- DANDI/Allen downloads at scale

Approved lab/vendor platform:
- first live BioGPU experiment
- live stimulation/closed-loop proof
```
