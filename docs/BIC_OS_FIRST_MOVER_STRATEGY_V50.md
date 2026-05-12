# BiC OS First-Mover Strategy v5.0

## Competitive reality

We are not alone in biological computing. Some platforms already provide hardware, APIs, closed-loop control, and organoid/MEA access. The project must not claim to be the first biological computer or the first wetware API.

## Where BiC OS can lead

BiC OS should aim to become the first broadly useful **vendor-neutral operating layer** for living neural compute workflows.

v5.10 turns this positioning into a local claim audit: the project is on-mission and local integrated architecture is supported, but global uniqueness is not proven by local tests and must remain a hypothesis until external prior-art work is done.

v5.11 turns the name **BiC OS** into a boot-readiness target: the current local system can be audited as an offline runtime kernel, while full production OS readiness remains blocked by durable daemon, auth, plugin, dashboard and live-lab layers.

v5.12 adds the missing discipline before OS: BiC OS should only be reached through a proven BioSDK / BioCompute Runtime evidence pack, with capability-level proof and explicit blockers for complete SDK and production OS claims.

v5.13 makes that discipline operational: BioSDK public core is the active phase, while BiC OS is locked until SDK examples, real external data/API validation, durable scheduling and release gates are complete.

v5.14 moves the proof path to sample acquisition: Zenodo local evidence is inventoried, while DANDI/NWB, Allen/public orientation, external read-only API/export and vendor/user-upload samples are tracked as required before stronger SDK or BiC OS claims.

v5.15 validates the first real DANDI/NWB task sample locally: units, trials, stimulus candidates and task-window export are now proven for one downloaded public NWB file, while external API/export and additional independent samples remain required.

v5.16 turns that DANDI/NWB sample into a public SDK benchmark example with spike-count/rate features and shuffled-label readout controls. This strengthens the BioSDK path but remains single-sample exploratory evidence.

v5.17 validates external read-only adapter contract behavior locally across mock FinalSpark, 3Brain, Axion and MCS clients, including write denial. Real external API/export proof still requires non-mock partner material.

v5.18 adds the Allen visual-coding orientation intake gate. This keeps the second independent public dataset proof explicit: current status is missing until a small Allen NWB/cache slice is placed under `data/external/allen/` and validates.

v5.19 adds vendor/user-upload read-only intake validation. This prepares the private beta data path without claiming vendor portability until a real safe export or user fixture passes the scanner.

v5.20 adds a real Allen visual-coding orientation benchmark from a capped DANDI `000021` session NWB. This strengthens the public BioSDK proof layer while preserving the BiC OS lock.

v5.21 adds a cross-dataset BioSDK evidence pack. It treats Zenodo, DANDI and Allen as the current public proof layer, while keeping external API/export and vendor/user-upload as explicit blockers before any full BioSDK or BiC OS claim.

v5.22 adds the public BioSDK examples gate. It turns the public proof layer into runnable examples and a runbook, while keeping real external/vendor material as the next evidence bottleneck.

v5.23 adds a safe user-upload fixture proof. It closes the local user-upload path but keeps vendor export and real external read-only API/export proof separate, preventing a premature full BioSDK or BiC OS claim.

The difference:

```text
Vertical wetware platform:
  own hardware + own API + own cloud

BiC OS target:
  multiple datasets + multiple wetware APIs + multiple vendors + LLM agents + benchmarks + evidence + safety + enterprise deployment
```

## First-mover goals

1. **NSI-1.0** — a neutral interface profile over NWB/HDF5/vendor APIs.
2. **Evidence Ledger** — signed/reproducible biological compute result bundles. v5.3 now provides local integrity signing, chained ledger hashes, ZIP safety checks and manifest-aware bundle validation for v24/v50 evidence bundles.
3. **LLM/Agent Bridge** — safe structured tasking for biological compute tools. v5.4 now provides an approval-aware tool catalog, policy review, NSI task-manifest emission for approved requests, claim-aware responses and blocked-by-default direct actuation.
4. **Adapter Conformance** — tests and certification for dataset/API/vendor adapters.
5. **Cross-dataset Benchmark Registry** — one benchmark language across public, vendor, and private datasets.
6. **Safety-graded Access Model** — maximum software access with blocked-by-default live actuation.
7. **Enterprise Control Plane** — hosted/on-prem job orchestration, audit, roles, quotas and bundles. v5.5 now provides the first offline admission bridge from approved agent/NSI manifests into the hosted beta queue model; durable persistence, workers and production auth remain future work.

## Commercially attractive wedge

The first product should not be “full biological OS”. The first product should be:

```text
BioSDK + BioCompute Runtime
for replay, read-only APIs, private data, benchmarks and evidence bundles.
```

Then:

```text
Hosted/On-Prem Control Plane
→ Live Shadow
→ Lab-Control Add-on
→ BiC OS
```

## What must be demonstrated

Before strong public claims:

- full_shuffle_1000;
- bootstrap confidence intervals;
- raw HDF5/TTL reconstruction and alignment (v5.6 maps 42 raw HDF5 files and embedded event candidates; v5.7 audits exact overlap and currently finds 0 exact raw/preprocessed recording matches, 3 shared LightStim targets and 19 temporal-signature matches; v5.8 builds a raw-native feature matrix from analog `ChannelData` windows with exploratory held-out-recording condition readout; v5.9 confirms raw event-window repeatability but blocks target-ID claims on the current sparse repeated-target subset);
- at least 3 independent dataset/API sources;
- adapter conformance tests;
- signed result bundles (local v5.3 integrity ledger exists; external identity/notarization remains future work);
- LLM safe-task demonstrator (v5.4 exists; MCP/server wrapper and hosted operator workflow remain future work);
- hosted server beta (v5.5 queue bridge exists; production persistence, workers, API-key auth and external beta deployment remain future work).
