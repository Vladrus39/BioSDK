# BioGPU-Core Master Project Plan v5.0

## Current identity

- **BioGPU-Core** — technical kernel and repository name.
- **BioSDK / Living Compute SDK** — developer SDK layer.
- **BioCompute Runtime** — near-term external product.
- **NSI-1.0 / Neural Substrate Interface** — interface standard draft.
- **BioCompute Control Plane** — hosted/on-prem server layer.
- **BiC OS** — long-term OS-like commercial target.

## Updated objective

Build a vendor-neutral BioCompute Runtime and future BiC OS for living neural compute, optimized for:

- LLM/agent workflows;
- experiments and benchmark orchestration;
- replay/read-only/live-shadow biological compute workflows;
- public and private neural data;
- vendor/API adapters;
- safety governance;
- reproducible evidence bundles;
- enterprise deployment.

## Current evidence base

- v12 spot-level response signal.
- v15 pulse-window feature matrix: 11,547 windows × 354 features.
- v32 real-data E2E replay above shuffled controls in fixed split.
- v33 compact paper-grade sweep.
- v36 lineage-strict split showing stricter, weaker but more honest signal.
- v46/v47 PC-ready evidence handoff.
- v5.4 safe LLM/Agent Bridge implemented for structured task review, NSI manifest emission and blocked-by-default live actuation.
- v5.5 Control Plane Queue Bridge implemented for admitting approved agent/NSI manifests into the hosted beta job model with tier and safety checks.
- v5.6 raw HDF5 structure/event inspection implemented: 42 Zenodo raw HDF5 files mapped, embedded EventStream candidates found, and first-pass raw stimulus-window preview generated.
- v5.7 raw-vs-preprocessed alignment audit implemented: v56 raw event candidates compared against v15 pulse metadata with exact-overlap, condition/target and temporal-signature status separation.
- v5.8 raw-native benchmark implemented: analog `ChannelData` event-window features extracted directly from raw HDF5 EventStream timestamps with held-out-recording condition readout.
- v5.9 raw-native stability audit implemented: v5.8 feature matrix tested for within-recording split-half repeatability and sparse repeated-target target-ID limits.
- v5.10 project alignment and claim audit implemented: local artifacts are checked against the BioCompute Runtime / BiC OS mission and unsafe uniqueness/first/live/GPU/energy claims are explicitly blocked.
- v5.11 BiC OS boot readiness implemented: NSI, evidence, agent bridge, queue, safety, raw-data runtime and claim supervisor are composed into an offline runtime-kernel boot manifest while production OS claims remain blocked.
- v5.12 BioSDK evidence pack implemented: v5.0-v5.11 artifacts are composed into a BioSDK capability matrix before any full BiC OS claim.
- v5.13 BioSDK core API implemented: public SDK facade exposes NSI validation, safe agent review, queue admission and phase gate while keeping BiC OS locked.
- v5.14 BioSDK sample acquisition gate implemented: local sample inventory, missing external proof sources, capped DANDI NWB download plan and BiC OS lock are machine-readable.
- v5.15 DANDI/NWB task validation implemented: downloaded DANDI NWB sample is inspected for units, trials, stimulus metadata and exported task windows.
- v5.16 DANDI/NWB SDK task benchmark implemented: the validated DANDI sample is converted into spike-count/rate features and a stratified shuffled-label readout example.
- v5.17 external read-only API/export gate implemented: all local mock API adapters export read-only traces and deny writes, while real partner/API proof remains blocked until a non-mock token or export is available.
- v5.18 Allen visual-coding orientation gate implemented: local Allen NWB/cache intake, unit/stimulus/orientation metadata inspection and capped-download discipline are tracked while the real Allen sample remains missing.
- v5.19 vendor/user-upload gate implemented: read-only sample intake, hash manifesting, schema hints, v4.2 importer routing and safety scanning are in place while real vendor/user fixtures remain missing.
- v5.20 Allen orientation benchmark implemented: the validated Allen visual-coding session is converted into bounded top-unit orientation features and shuffled-label readout evidence.
- v5.21 cross-dataset BioSDK evidence pack implemented: Zenodo raw HDF5, DANDI NWB, Allen visual coding, external read-only and vendor/user-upload blockers are summarized in one proof matrix.
- v5.22 BioSDK public examples gate implemented: the proven public path is packaged as runnable examples, catalog and runbook while external/vendor examples remain blocked handoffs.
- v5.23 safe user-upload fixture implemented: a read-only user fixture validates the v5.19 upload path and refreshes v5.14/v5.21/v5.22 while real external API/export remains blocked.
- v5.24 external export validation implemented: a small official MCS HDF5 RawData fixture is validated as non-secret read-only external export evidence, refreshing v5.17/v5.14/v5.21/v5.22 while live API/control claims remain blocked.
- v5.25 BioSDK release-candidate evidence package implemented: v5.12-v5.24 proofs are gathered into a checklist, manifest and report for RC review while full BioSDK, BioCompute Runtime and BiC OS claims remain blocked.
- v5.26 durable scheduler/worker proof implemented: v5.5-admitted safe jobs are persisted into SQLite, reopened after scheduler restart, claimed by a local worker and completed with local result artifacts while production runtime and BiC OS claims remain blocked.
- v5.27 scheduler API facade implemented: the durable queue now has local list/get/cancel/retry/timeout/worker-step semantics and route manifest proof while authenticated production API, hosted runtime and BiC OS claims remain blocked.
- v5.28 authenticated local service proof implemented: v5.27 scheduler operations now have local fixture API-key auth, scope checks and result-bundle download checksum validation while production service/runtime and BiC OS claims remain blocked.
- v5.29 supervised local runtime proof implemented: the authenticated local service now has start/heartbeat/worker-tick/graceful-shutdown/audit-export lifecycle evidence while production daemon/runtime and BiC OS claims remain blocked.
- v5.30 runtime observability proof implemented: the supervised local runtime now has metrics snapshots, status snapshots and non-destructive audit retention policy evidence while production observability/runtime and BiC OS claims remain blocked.
- v5.31 recovery alerting proof implemented: local stale-heartbeat alerts, worker timeout classification, retry recovery and recovery audit bundle evidence are in place while production monitoring/recovery and BiC OS claims remain blocked.
- v5.32 bounded retry/dead-letter proof implemented: local retry attempt limits, deterministic backoff metadata and terminal dead-letter audit entries are in place while production retry orchestration/recovery and BiC OS claims remain blocked.
- v5.33 operator incident retention proof implemented: local dead-letter incidents now have operator acknowledgement, resolution transitions, non-destructive retention export and incident audit bundle evidence while production incident management and BiC OS claims remain blocked.
- v5.34 tamper-evident incident ledger proof implemented: local incident lifecycle records now have append-only chained hashes, local signatures, retention-manifest anchoring and tamper-detection evidence while production notarization/storage and BiC OS claims remain blocked.
- v5.35 tenant incident permissions proof implemented: local fixture-scoped tenant roles, incident action scopes, viewer write denial, cross-tenant denial and ledger-validation scope evidence are in place while production auth and BiC OS claims remain blocked.
- v5.36 dashboard route-contract proof implemented: local dashboard route manifest, DTO/view payloads and role/scope access probes are validated over v5.35 permissions while hosted dashboard, production auth and BiC OS claims remain blocked.
- v5.37 identity-provider contract proof implemented: local OIDC discovery/JWKS/claims validation, key-rotation contract, role/scope mapping and dashboard access probes are validated while real IdP configuration, production auth and BiC OS claims remain blocked.
- v5.38 storage retention contract proof implemented: local object-storage bucket contracts, object integrity manifest, retention metadata, local access contracts and immutable-root overwrite denial are validated while production storage and BiC OS claims remain blocked.
- v5.39 packaged SDK install gate implemented: package metadata, package discovery, critical CLI entrypoints, local wheel build and installed-package import smoke are validated while published distribution, full BioSDK and BiC OS claims remain blocked.
- v5.40 private beta onboarding contract implemented: local release handoff boundaries, onboarding artifacts, rollback/support contract and read-only participant gate are validated while external beta, full BioSDK and BiC OS claims remain blocked.
- v5.41 clean-room install report contract implemented: local isolated-target install probe, report section contract and completeness checks are validated while independent external clean-room report, full BioSDK and BiC OS claims remain blocked.
- v5.42 signed artifact provenance contract implemented: local wheel artifact hashing, provenance statement, local HMAC-style signature validation and tamper detection are validated while trusted external signing, transparency log, full BioSDK and BiC OS claims remain blocked.
- v5.43 release approval and revocation contract implemented: local reviewer approval matrix, local release-candidate decision record and revocation drill are validated while production release, public registry distribution, full BioSDK and BiC OS claims remain blocked.
- v5.44 private registry handoff contract implemented: local approved wheel staging, dry-run private registry index, handoff access matrix and revocation denial are validated while live private registry, production distribution, full BioSDK and BiC OS claims remain blocked.
- v5.45 recipient onboarding audit contract implemented: local recipient approvals, named-account fixtures, access-log chaining and expiry denial are validated while real recipient onboarding, live private registry accounts, production distribution, full BioSDK and BiC OS claims remain blocked.
- v5.46 private registry auth/feed contract implemented: local token scope/signature checks, expiring-feed manifest/probe and registry-log export shape are validated while real private registry auth, live registry feed enforcement, production distribution, full BioSDK and BiC OS claims remain blocked.
- v5.47 registry revoke/yank notification contract implemented: local revoke/yank decision matrix, token/feed disable manifest, recipient notification acknowledgement trail, post-yank denial probe and incident linkage export are validated while production yank authority, live registry revocation, real notification delivery, full BioSDK and BiC OS claims remain blocked.
- v5.48 release operations handoff contract implemented: local release runbook sections, operator handoff checklist matrix, handoff packet signatures and claim-boundary attestations are validated while production release operations, full BioSDK and BiC OS claims remain blocked; many additional proof layers remain before production or OS readiness.
- v5.49 production readiness gap contract implemented: 12 production readiness domains are mapped as open gaps, staged local pilot acceptance records are validated and every production/external-pilot/full BioSDK/BiC OS claim remains blocked until real services, approvals and external acceptance evidence exist.
- v5.50 external acceptance intake contract implemented: local external acceptance evidence schema, evidence matrix, packet shape, real-pilot intake gate and blocker register are validated while real acceptance records, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.
- v5.51 partner data-room review packet contract implemented: local partner data-room manifest, local external review packet, review preflight gate and blocker register are validated while real data-room upload, completed external review, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.
- v5.52 external reviewer response intake contract implemented: local questionnaire scoring, signed review-response packet shape, signed-response intake gate and blocker register are validated while real signed review responses, completed external review, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.
- v5.53 external review finding triage contract implemented: local finding triage matrix, remediation-plan packet shape, closure preflight gate and blocker register are validated while real finding closure, completed external review, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.
- v5.54 remediation evidence closure contract implemented: local remediation evidence verification matrix, closure attestation packet shape, closure-attestation preflight gate and blocker register are validated while real closure attestations, real finding closure, completed external review, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.
- v5.55 closure signoff registry contract implemented: local closure attestation audit trail, external reviewer signoff registry matrix, signoff packet shape, signoff-registry preflight gate and blocker register are validated while real external reviewer signoff, real closure signoff, real finding closure, completed external review, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.
- v5.56 external signoff transcript intake contract implemented: local intake contract for real external reviewer signoff payloads, signed closure transcript packet shape, transcript acceptance gate and blocker register are validated while real signoff acceptance, signed transcript acceptance, real finding closure, completed external review, real external pilot, production readiness, full BioSDK and BiC OS claims remain blocked.

## Next development sequence

### PC validation phase

1. Repeat smoke and compact checks.
2. Validate full `Pre_processed_MEA_data.zip`.
3. Run v33 compact and v36 lineage compact.
4. Run full_shuffle_1000.
5. Run extended_methods_5000.
6. Add bootstrap confidence intervals.
7. Package PC result bundle.

### Dataset/API expansion phase

1. Zenodo raw HDF5 / TTL reconstruction. v5.6 maps raw HDF5 structure and embedded event streams; v5.7 audits raw/preprocessed coverage and shows no exact recording overlap in the current local subsets; v5.8 builds a raw-native event-window feature benchmark directly from raw `ChannelData`; v5.9 confirms very high within-recording repeatability while showing target-ID signal is not supported on the sparse repeated-target subset. Next: get stronger repeated-target raw coverage or resolve exact raw coverage for v15 rows.
2. DANDI/NWB parser. v5.15 validates one real downloaded DANDI NWB sample with units, trials, stimulus candidates and task-window export. v5.16 turns that sample into a public SDK benchmark example with shuffled-label controls.
3. Public BioSDK example layer. v5.18 validates a local Allen/DANDI visual-coding session, v5.20 turns it into a bounded orientation benchmark, v5.21 aggregates Zenodo/DANDI/Allen proof, and v5.22 packages that public proof as runnable SDK examples.
4. FinalSpark/export read-only adapter validation. v5.17 validates local read-only adapter contracts and write denial; v5.24 adds one validated read-only external export fixture, while live API/token access remains a separate future proof.
5. Vendor export adapter tests. v5.19 adds read-only intake validation and safety scanning; real safe vendor exports are still required.
6. User-uploaded data import validation. v5.19 adds user-upload fixture validation; private beta proof still needs a safe user sample.
7. v5.14 adds a sample acquisition gate so these downloads/credentials are tracked before full SDK proof claims.

### NSI/interface phase

1. Freeze NSI-1.0 schemas.
2. Implement adapter conformance tests.
3. Implement result bundle validator.
4. Implement claim-level annotation. v5.10 adds a project-level claim register that marks global uniqueness as not locally provable and blocks first-biological-computer/live/GPU/energy overclaims.
5. Write developer adapter guide.

### Hosted/private beta phase

1. Hosted server real job queue. Initial offline queue bridge exists in v5.5; production persistence/workers remain future work.
2. User roles and API keys.
3. Dataset uploads and storage.
4. Result-bundle retention.
5. Private beta onboarding.
6. Enterprise pilot pack.

### BioSDK proof phase

1. Maintain a machine-readable BioSDK capability matrix. v5.12 starts this with PC evidence, dataset import, NSI, ledger, agent bridge, control-plane admission, raw-data runtime, claim supervisor and BiC OS bridge.
2. Add public SDK examples for every NSI schema and supported adapter contract. v5.13 starts this with a minimal public facade and reference replay flow.
3. Add durable scheduler/worker execution so SDK jobs are repeatable beyond in-memory demos. v5.26 proves a local SQLite-backed queue and worker lifecycle; v5.27 adds local API facade semantics for list/get/cancel/retry/timeout/worker-step; v5.28 adds local fixture API-key auth, scope checks and result-bundle download checksum validation; v5.29 adds supervised local lifecycle state, heartbeat, graceful shutdown and audit export; v5.30 adds local metrics snapshots and non-destructive audit retention policy proof; v5.31 adds stale-heartbeat alerting and worker timeout recovery proof; v5.32 adds bounded retry limits, deterministic backoff metadata and dead-letter audit entries; v5.33 adds operator acknowledgement, incident resolution and non-destructive incident retention export; v5.34 adds append-only incident ledger hashes, local signatures, retention-manifest anchoring and tamper-detection proof; v5.35 adds fixture-scoped tenant roles, action scopes, cross-tenant denial and viewer write denial; v5.36 adds dashboard route contracts, DTO/view payloads and access probes over the permission layer; v5.37 adds OIDC discovery/JWKS/claims validation and role/scope mapping contract proof; v5.38 adds object-storage bucket contracts, object integrity manifests, retention metadata and immutable-root overwrite denial. Production API, multi-worker deployment, hosted storage, production retry orchestration, real identity provider integration, persistent tenant membership, hosted dashboard enforcement and production incident notarization remain future work.
4. Validate at least one real NWB/DANDI asset and one external read-only adapter/API path. v5.14 starts this by producing a capped DANDI NWB sample download plan and marking external read-only API/export as required.
5. Package an installable SDK release candidate with docs, examples, gates and evidence bundle. v5.25 packages the RC evidence checklist and manifest; v5.39 adds a local wheel build/install smoke gate; v5.40 adds a local private-beta onboarding and release-operations contract; v5.41 adds a local clean-room install reporting contract and local isolated-target install probe; v5.42 adds local wheel artifact hashing, provenance statement, local signature validation and tamper detection; v5.43 adds local release-candidate approval and revocation contract proof; v5.44 adds local artifact handoff staging, dry-run private registry indexing, access decisions and revocation denial; v5.45 adds local recipient onboarding approvals, access-log chaining and expiry denial; v5.46 adds local auth token/feed expiry semantics and registry log export shape; v5.47 adds a local registry revoke/yank drill, token/feed disable manifest, recipient notification acknowledgements and incident linkage export; v5.48 adds a local release operations runbook, operator handoff packet and claim-boundary attestation proof; v5.49 adds a production readiness gap matrix and staged local pilot acceptance contract with all 12 production domains still blocked; v5.50 adds a local external acceptance evidence schema, evidence matrix, packet shape, real-pilot intake gate and blocker register with real acceptance records still at zero; v5.51 adds a local partner data-room manifest, external review packet shape, review preflight gate and external-review blocker register with completed external reviews still at zero; v5.52 adds local external reviewer questionnaire scoring, signed review-response packet shape, signed-response intake gate and blocker register with real signed responses still at zero; v5.53 adds local external review finding triage, remediation-plan packet shape, closure preflight gate and blocker register with real finding closures still at zero; v5.54 adds local remediation evidence verification, closure attestation packet shape, closure-attestation preflight gate and blocker register with real closure attestations still at zero; v5.55 adds a local closure attestation audit trail, external reviewer signoff registry matrix, signoff packet shape, signoff-registry preflight gate and blocker register with real external reviewer signoffs, real closure signoffs and closed findings still at zero; v5.56 adds local external signoff intake, signed closure transcript packet shape, transcript acceptance gate and blocker register with real signoff acceptance, transcript acceptance and closed findings still at zero. Published distribution, live private registry/auth integration, trusted release signing, external provenance attestation, transparency-log inclusion, independent external clean-room validation, real participant approvals/access logs, registry-enforced signed URL or feed expiry, production notification delivery, production release operations, external pilot acceptance, signed closure transcript acceptance and production rollback/yank authority remain future work.

### BiC OS phase

1. Runtime daemon. v5.11 composes an offline runtime-kernel boot manifest; durable daemon/workers remain future work.
2. Scheduler.
3. Permission system.
4. Plugin manager.
5. Dashboard.
6. Evidence ledger.
7. Safety supervisor.
8. Lab approval workflow.
9. Live telemetry.
10. Lab-approved closed-loop module.

## Progress log

### 2026-05-07 — v5.28 Authenticated local service proof

- Implemented `biogpu/runtime/local_service_v528.py`: a local authenticated service contract over v5.27 with non-secret fixture API keys, explicit scopes, missing/invalid auth rejection, worker-step authorization and local result-bundle download checksum validation.
- Added `biogpu/benchmarks/biogpu_v528_authenticated_local_service.py`, `scripts/run_biogpu_v528_authenticated_local_service.ps1`, `tests/current/test_biogpu_v528_authenticated_local_service.py`, `docs/AUTHENTICATED_LOCAL_SERVICE_GUIDE_V528.md` and `examples/biosdk_v528_authenticated_local_service.py`.
- v5.28 gate passed with `authenticated_local_service_ready=true`, `auth_required_for_v1=true`, `scope_denial_passed=true`, `result_bundle_download_contract_passed=true`, `production_api_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.28. This advances BioCompute Runtime evidence without claiming production service readiness, full BioSDK readiness or BiC OS readiness.

### 2026-05-07 — v5.29 Supervised local runtime lifecycle proof

- Implemented `biogpu/runtime/supervised_runtime_v529.py`: a deterministic in-process supervisor over v5.28 with runtime state file, heartbeat file, worker ticks, graceful shutdown, post-shutdown worker rejection and JSONL audit export.
- Added `biogpu/benchmarks/biogpu_v529_supervised_runtime.py`, `scripts/run_biogpu_v529_supervised_runtime.ps1`, `tests/current/test_biogpu_v529_supervised_runtime.py`, `docs/SUPERVISED_LOCAL_RUNTIME_GUIDE_V529.md` and `examples/biosdk_v529_supervised_runtime.py`.
- v5.29 remains a local lifecycle proof only: production daemon installation, restart policy, hosted deployment, tenant audit retention, production object storage and BiC OS readiness remain blockers.

### 2026-05-07 — v5.30 Runtime observability and retention proof

- Implemented `biogpu/runtime/observability_v530.py`: local metrics snapshots over the v5.29 supervisor, status snapshots across lifecycle actions, and a non-destructive audit retention policy with full export before pruning.
- Added `biogpu/benchmarks/biogpu_v530_runtime_observability.py`, `scripts/run_biogpu_v530_runtime_observability.ps1`, `tests/current/test_biogpu_v530_runtime_observability.py`, `docs/RUNTIME_OBSERVABILITY_GUIDE_V530.md` and `examples/biosdk_v530_runtime_observability.py`.
- v5.30 gate passed with `runtime_observability_ready=true`, `local_metrics_snapshot_ready=true`, `status_snapshot_count=9`, `retention_policy_contract_ready=true`, `pruned_audit_event_count=2`, `production_metrics_ready=false` and `bic_os_phase_locked=true`.
- v5.30 remains a local observability proof only: production metrics backend, tenant audit retention, alerting, hosted dashboards, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.31 Recovery alerting proof

- Implemented `biogpu/runtime/recovery_v531.py`: stale-heartbeat alert classification, worker timeout failure classification, retry-based recovery using the durable scheduler facade, and recovery audit bundle export.
- Added `biogpu/benchmarks/biogpu_v531_recovery_alerting.py`, `scripts/run_biogpu_v531_recovery_alerting.ps1`, `tests/current/test_biogpu_v531_recovery_alerting.py`, `docs/RECOVERY_ALERTING_GUIDE_V531.md` and `examples/biosdk_v531_recovery_alerting.py`.
- v5.31 gate passed with `recovery_alerting_ready=true`, `stale_heartbeat_alert_passed=true`, `failure_classification_passed=true`, `worker_recovery_passed=true`, `recovery_audit_bundle_ready=true`, `production_recovery_ready=false` and `bic_os_phase_locked=true`.
- v5.31 remains a local recovery proof only: production monitor loops, paging, worker crash supervision, bounded retry/dead-letter queues, hosted dashboards, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.32 Bounded retry and dead-letter proof

- Implemented `biogpu/runtime/retry_policy_v532.py`: a local retry policy wrapper over the durable scheduler facade with max-attempt enforcement, deterministic backoff metadata, terminal dead-letter marking and retry policy audit bundle export.
- Added `biogpu/benchmarks/biogpu_v532_bounded_retry_dead_letter.py`, `scripts/run_biogpu_v532_bounded_retry_dead_letter.ps1`, `tests/current/test_biogpu_v532_bounded_retry_dead_letter.py`, `docs/BOUNDED_RETRY_DEAD_LETTER_GUIDE_V532.md` and `examples/biosdk_v532_bounded_retry_dead_letter.py`.
- v5.32 gate passed with `bounded_retry_dead_letter_ready=true`, `bounded_retry_policy_ready=true`, `dead_letter_queue_ready=true`, `max_attempts_enforced=true`, `retry_backoff_metadata_ready=true`, `production_retry_policy_ready=false` and `bic_os_phase_locked=true`.
- v5.32 remains a local recovery-policy proof only: production retry orchestration, durable timer workers, process crash supervision, operator acknowledgement, hosted incident dashboards, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.33 Operator incident retention proof

- Implemented `biogpu/runtime/incident_workflow_v533.py`: local dead-letter incidents, operator acknowledgement, resolution transitions, non-destructive incident retention export, archived resolved incident handling and incident audit bundle export.
- Added `biogpu/benchmarks/biogpu_v533_operator_incident_retention.py`, `scripts/run_biogpu_v533_operator_incident_retention.ps1`, `tests/current/test_biogpu_v533_operator_incident_retention.py`, `docs/OPERATOR_INCIDENT_RETENTION_GUIDE_V533.md` and `examples/biosdk_v533_operator_incident_retention.py`.
- v5.33 gate passed with `operator_incident_retention_ready=true`, `operator_acknowledgement_ready=true`, `incident_resolution_ready=true`, `incident_retention_manifest_ready=true`, `incident_audit_bundle_ready=true`, `production_incident_retention_ready=false` and `bic_os_phase_locked=true`.
- v5.33 remains a local incident workflow proof only: production operator permissions, hosted paging, tamper-evident incident storage, tenant-aware retention, dashboards, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.34 Tamper-evident incident ledger proof

- Implemented `biogpu/runtime/incident_ledger_v534.py`: incident lifecycle source records, append-only ledger entries, chained hashes, local HMAC-style signatures, retention-manifest anchoring, validation and tamper-detection probe.
- Added `biogpu/benchmarks/biogpu_v534_tamper_evident_incident_ledger.py`, `scripts/run_biogpu_v534_tamper_evident_incident_ledger.ps1`, `tests/current/test_biogpu_v534_tamper_evident_incident_ledger.py`, `docs/TAMPER_EVIDENT_INCIDENT_LEDGER_GUIDE_V534.md` and `examples/biosdk_v534_tamper_evident_incident_ledger.py`.
- v5.34 gate passed with `tamper_evident_incident_ledger_ready=true`, `incident_ledger_chain_valid=true`, `local_signature_validation_ready=true`, `retention_manifest_anchored=true`, `tamper_detection_passed=true`, `incident_ledger_bundle_ready=true`, `production_incident_ledger_ready=false` and `bic_os_phase_locked=true`.
- v5.34 remains a local incident ledger proof only: external notarization, hosted append-only storage, tenant operator permissions, paging integrations, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.35 Tenant incident permissions proof

- Implemented `biogpu/runtime/incident_permissions_v535.py`: local fixture principals, tenant-scoped incident action authorization, viewer write denial, cross-tenant operator denial, incident-admin/auditor ledger validation and permission audit bundle export.
- Added `biogpu/benchmarks/biogpu_v535_tenant_incident_permissions.py`, `scripts/run_biogpu_v535_tenant_incident_permissions.ps1`, `tests/current/test_biogpu_v535_tenant_incident_permissions.py`, `docs/TENANT_INCIDENT_PERMISSIONS_GUIDE_V535.md` and `examples/biosdk_v535_tenant_incident_permissions.py`.
- v5.35 gate passed with `tenant_incident_permissions_ready=true`, `permission_matrix_ready=true`, `tenant_isolation_passed=true`, `viewer_write_denial_passed=true`, `ledger_validation_scope_passed=true`, `production_auth_ready=false` and `bic_os_phase_locked=true`.
- v5.35 remains a local permission proof only: production identity provider integration, key rotation, persistent tenant membership, hosted auth enforcement, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.36 Dashboard route-contract proof

- Implemented `biogpu/runtime/dashboard_routes_v536.py`: local dashboard route contracts, DTO/view payloads, permission-aware access probes and audit bundle export over the v5.35 tenant incident permissions layer.
- Added `biogpu/benchmarks/biogpu_v536_dashboard_route_contract.py`, `scripts/run_biogpu_v536_dashboard_route_contract.ps1`, `tests/current/test_biogpu_v536_dashboard_route_contract.py`, `docs/DASHBOARD_ROUTE_CONTRACT_GUIDE_V536.md` and `examples/biosdk_v536_dashboard_route_contract.py`.
- v5.36 gate passed with `dashboard_route_contract_ready=true`, `route_count=9`, `dashboard_access_matrix_ready=true`, `viewer_write_denial_passed=true`, `tenant_isolation_passed=true`, `production_dashboard_ready=false`, `production_auth_ready=false` and `bic_os_phase_locked=true`.
- v5.36 remains a local route-contract proof only: hosted dashboard server, browser session enforcement, production identity, object storage, immutable ledger storage, monitoring, lab approval workflow, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.37 Identity-provider contract proof

- Implemented `biogpu/runtime/identity_provider_contract_v537.py`: local OIDC discovery contract, JWKS rotation contract, token claim validation, role/scope mapping and dashboard access probes over the v5.36 dashboard route layer.
- Added `biogpu/benchmarks/biogpu_v537_identity_provider_contract.py`, `scripts/run_biogpu_v537_identity_provider_contract.ps1`, `tests/current/test_biogpu_v537_identity_provider_contract.py`, `docs/IDENTITY_PROVIDER_CONTRACT_GUIDE_V537.md` and `examples/biosdk_v537_identity_provider_contract.py`.
- v5.37 gate passed with `identity_provider_contract_ready=true`, `oidc_discovery_contract_ready=true`, `jwks_rotation_contract_ready=true`, `identity_validation_matrix_ready=true`, `identity_dashboard_access_ready=true`, `production_auth_ready=false` and `bic_os_phase_locked=true`.
- v5.37 remains a local identity contract proof only: no real OIDC/OAuth provider config or token was found locally, and real discovery/JWKS endpoints, issuer/audience values, hosted app registration, persistent tenant membership, dashboard session policy, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.38 Storage retention contract proof

- Implemented `biogpu/runtime/storage_retention_v538.py`: local object-storage bucket contracts, JSON object writes, SHA-256 integrity manifest, local access contracts, retention metadata and immutable-root overwrite denial over the v5.37 identity contract layer.
- Added `biogpu/benchmarks/biogpu_v538_storage_retention_contract.py`, `scripts/run_biogpu_v538_storage_retention_contract.ps1`, `tests/current/test_biogpu_v538_storage_retention_contract.py`, `docs/STORAGE_RETENTION_CONTRACT_GUIDE_V538.md` and `examples/biosdk_v538_storage_retention_contract.py`.
- v5.38 gate passed with `storage_retention_contract_ready=true`, `storage_object_integrity_ready=true`, `retention_manifest_ready=true`, `local_access_contract_ready=true`, `immutable_overwrite_denial_ready=true`, `production_object_storage_ready=false` and `bic_os_phase_locked=true`.
- v5.38 remains a local storage contract proof only: no production object-storage config was found locally, and real bucket/account setup, IAM policy, server-side encryption, retention locks, remote immutable ledger storage/notarization, backup/restore evidence, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.39 Packaged SDK install gate

- Implemented `biogpu/sdk/package_install_gate_v539.py`: package metadata validation, `biogpu*` package discovery, critical CLI entrypoint import/callable probes, distribution manifest hashing, optional local wheel build and installed-package import smoke over the v5.38 storage contract layer.
- Added `biogpu/benchmarks/biogpu_v539_packaged_sdk_install_gate.py`, `scripts/run_biogpu_v539_packaged_sdk_install_gate.ps1`, `tests/current/test_biogpu_v539_packaged_sdk_install_gate.py`, `docs/PACKAGED_SDK_INSTALL_GATE_GUIDE_V539.md` and `examples/biosdk_v539_packaged_sdk_install_gate.py`.
- v5.39 gate initially exposed a missing local build toolchain (`setuptools.build_meta` unavailable); after installing the declared build requirements `setuptools>=68` and `wheel`, the gate passed with `packaged_sdk_install_gate_ready=true`, `package_metadata_contract_ready=true`, `entrypoint_contract_ready=true`, `local_wheel_build_ready=true`, `local_install_smoke_ready=true`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- v5.39 remains a local install gate only: published package registry/private index, signed artifacts, provenance attestation, clean-room install validation, versioned documentation, release approval/rollback operations, full BioSDK readiness, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.40 Private beta onboarding contract

- Implemented `biogpu/sdk/private_beta_onboarding_v540.py`: local private-beta handoff boundaries, required onboarding artifacts, release operations/rollback support contract and participant decision matrix over the v5.39 install gate.
- Added `biogpu/benchmarks/biogpu_v540_private_beta_onboarding.py`, `scripts/run_biogpu_v540_private_beta_onboarding.ps1`, `tests/current/test_biogpu_v540_private_beta_onboarding.py`, `docs/PRIVATE_BETA_ONBOARDING_GUIDE_V540.md` and `examples/biosdk_v540_private_beta_onboarding.py`.
- v5.40 gate passed with `private_beta_onboarding_contract_ready=true`, `v539_dependency_ready=true`, `release_operations_contract_ready=true`, `participant_gate_ready=true`, `allowed_participant_count=3`, `denied_participant_count=4`, `external_beta_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- v5.40 remains a local onboarding contract proof only: named participants with signed agreements, approved private artifact handoff or registry, signed/provenance release artifacts, external clean-room install reports, support roster approval, production incident/rollback authority, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.41 Clean-room install report contract

- Implemented `biogpu/sdk/clean_room_install_report_v541.py`: local clean-room environment contract, report section requirements, report completeness validation, optional local wheel build/target-install probe and report fixture hashing over the v5.40 onboarding contract.
- Added `biogpu/benchmarks/biogpu_v541_clean_room_install_report.py`, `scripts/run_biogpu_v541_clean_room_install_report.ps1`, `tests/current/test_biogpu_v541_clean_room_install_report.py`, `docs/CLEAN_ROOM_INSTALL_REPORT_GUIDE_V541.md` and `examples/biosdk_v541_clean_room_install_report.py`.
- v5.41 gate passed with `clean_room_install_report_contract_ready=true`, `v540_dependency_ready=true`, `environment_contract_ready=true`, `report_completeness_ready=true`, `local_clean_room_install_probe_ready=true`, `external_clean_room_report_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- v5.41 remains a local reporting contract proof only: independent machine/CI runner, signed tester identity or attestation, approved private artifact handoff, full fresh-environment command transcript, network isolation/dependency cache evidence, external beta participant approvals, signed artifact provenance, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.42 Signed artifact provenance contract

- Implemented `biogpu/sdk/artifact_provenance_v542.py`: local provenance policy, wheel artifact manifest, provenance statement, local HMAC-style signature envelope, signature validation and tamper-detection probe over the v5.41 clean-room install report.
- Added `biogpu/benchmarks/biogpu_v542_signed_artifact_provenance.py`, `scripts/run_biogpu_v542_signed_artifact_provenance.ps1`, `tests/current/test_biogpu_v542_signed_artifact_provenance.py`, `docs/SIGNED_ARTIFACT_PROVENANCE_GUIDE_V542.md` and `examples/biosdk_v542_signed_artifact_provenance.py`.
- v5.42 gate passed with `signed_artifact_provenance_contract_ready=true`, `v541_dependency_ready=true`, `artifact_manifest_ready=true`, `local_signature_ready=true`, `signature_validation_ready=true`, `tamper_detection_ready=true`, `trusted_external_signature_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- v5.42 remains a local provenance proof only: trusted release signing identity or hardware-backed key, external provenance attestation from an independent clean-room runner, transparency log or immutable release ledger inclusion, approved artifact handoff/registry, signed checksum publication, release approval/revocation policy, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.43 Release approval and revocation contract

- Implemented `biogpu/sdk/release_approval_v543.py`: local release approval policy, reviewer approval/denial matrix, revocation policy, revocation drill and local release-candidate decision record over the v5.42 provenance contract.
- Added `biogpu/benchmarks/biogpu_v543_release_approval_revocation.py`, `scripts/run_biogpu_v543_release_approval_revocation.ps1`, `tests/current/test_biogpu_v543_release_approval_revocation.py`, `docs/RELEASE_APPROVAL_REVOCATION_GUIDE_V543.md` and `examples/biosdk_v543_release_approval_revocation.py`.
- v5.43 gate passed with `release_approval_revocation_contract_ready=true`, `v542_dependency_ready=true`, `release_approval_matrix_ready=true`, `release_revocation_drill_ready=true`, `local_candidate_handoff_approved=true`, `production_release_approved=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- v5.43 remains a local release-candidate contract proof only: named release authority, trusted signing/revocation key management, approved registry or artifact handoff channel, external clean-room/provenance attestation, transparency log or immutable release ledger inclusion, production rollback/yank/user notification authority, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.44 Private registry handoff contract

- Implemented `biogpu/sdk/private_registry_handoff_v544.py`: local private-registry/artifact handoff contract, approved wheel artifact record, staged local handoff package, dry-run private registry index, access matrix and revoked-access probe over the v5.43 release approval layer.
- Added `biogpu/benchmarks/biogpu_v544_private_registry_handoff.py`, `scripts/run_biogpu_v544_private_registry_handoff.ps1`, `tests/current/test_biogpu_v544_private_registry_handoff.py`, `docs/PRIVATE_REGISTRY_HANDOFF_GUIDE_V544.md` and `examples/biosdk_v544_private_registry_handoff.py`.
- v5.44 gate passed with `private_registry_handoff_contract_ready=true`, `v543_dependency_ready=true`, `local_handoff_package_ready=true`, `handoff_access_matrix_ready=true`, `handoff_revocation_probe_ready=true`, `local_registry_index_ready=true`, `live_private_registry_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.44. v5.44 remains a local handoff/dry-run registry contract only: actual private registry or artifact repository, registry auth integration, named recipient accounts, signed URL/feed expiration, artifact retention/audit export, production registry yank/revoke authority, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.45 Recipient onboarding audit contract

- Implemented `biogpu/sdk/recipient_onboarding_audit_v545.py`: local recipient onboarding policy, approval/denial matrix, named-account fixture validation, chained local access log, expiry denial probe and recipient audit bundle over the v5.44 private-registry handoff contract.
- Added `biogpu/benchmarks/biogpu_v545_recipient_onboarding_audit.py`, `scripts/run_biogpu_v545_recipient_onboarding_audit.ps1`, `tests/current/test_biogpu_v545_recipient_onboarding_audit.py`, `docs/RECIPIENT_ONBOARDING_AUDIT_GUIDE_V545.md` and `examples/biosdk_v545_recipient_onboarding_audit.py`.
- v5.45 gate passed with `recipient_onboarding_audit_contract_ready=true`, `v544_dependency_ready=true`, `recipient_onboarding_matrix_ready=true`, `recipient_access_log_ready=true`, `access_expiry_probe_ready=true`, `recipient_audit_bundle_ready=true`, `real_recipient_onboarding_ready=false`, `live_private_registry_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.45. v5.45 remains a local recipient onboarding audit proof only: real recipient identities and organization approvals, private registry account provisioning, registry auth integration, signed URL/private feed expiry enforcement, registry access-log export/retention, recipient notification trail, production revoke/yank authority, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.46 Private registry auth/feed contract

- Implemented `biogpu/sdk/private_registry_auth_feed_v546.py`: local private-registry auth/feed policy, token scope/signature matrix, expiring private-feed manifest, expired-feed denial probe, registry log export contract and auth/feed audit bundle over the v5.45 recipient onboarding audit contract.
- Added `biogpu/benchmarks/biogpu_v546_private_registry_auth_feed.py`, `scripts/run_biogpu_v546_private_registry_auth_feed.ps1`, `tests/current/test_biogpu_v546_private_registry_auth_feed.py`, `docs/PRIVATE_REGISTRY_AUTH_FEED_GUIDE_V546.md` and `examples/biosdk_v546_private_registry_auth_feed.py`.
- v5.46 gate passed with `private_registry_auth_feed_contract_ready=true`, `v545_dependency_ready=true`, `auth_feed_matrix_ready=true`, `expiring_feed_manifest_ready=true`, `expiring_feed_probe_ready=true`, `registry_log_export_contract_ready=true`, `real_private_registry_auth_ready=false`, `live_private_registry_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.46. v5.46 remains a local auth/feed contract proof only: live private registry endpoint/feed, registry auth provider integration, real account provisioning/token issuance, registry-enforced feed expiry, registry access-log export/retention backend, recipient notification trail, production revoke/yank authority, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.47 Registry revoke/yank notification contract

- Implemented `biogpu/sdk/registry_revoke_yank_notification_v547.py`: local registry revoke/yank policy, decision matrix, token/feed disable manifest, recipient notification acknowledgement trail, post-yank access denial probe, incident linkage export and audit bundle over the v5.46 private registry auth/feed contract.
- Added `biogpu/benchmarks/biogpu_v547_registry_revoke_yank_notification.py`, `scripts/run_biogpu_v547_registry_revoke_yank_notification.ps1`, `tests/current/test_biogpu_v547_registry_revoke_yank_notification.py`, `docs/REGISTRY_REVOKE_YANK_NOTIFICATION_GUIDE_V547.md` and `examples/biosdk_v547_registry_revoke_yank_notification.py`.
- v5.47 gate passed with `registry_revoke_yank_notification_contract_ready=true`, `v546_dependency_ready=true`, `revoke_yank_matrix_ready=true`, `local_yank_manifest_ready=true`, `recipient_notification_ack_trail_ready=true`, `revoke_yank_effect_probe_ready=true`, `incident_linkage_export_ready=true`, `production_yank_ready=false`, `live_private_registry_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.47. v5.47 remains a local revoke/yank notification drill only: live private registry revoke/yank endpoint, production token revocation and package yank authority, notification provider integration, real recipient acknowledgement collection, registry access-log retention/export, production incident workflow, full BioSDK, production runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.48 Release operations handoff contract

- Implemented `biogpu/sdk/release_operations_handoff_v548.py`: local release operations policy, runbook sections, operator handoff allow/deny matrix, local handoff packet signatures, claim-boundary attestations and release-ops audit bundle over the v5.47 registry revoke/yank notification contract.
- Added `biogpu/benchmarks/biogpu_v548_release_operations_handoff.py`, `scripts/run_biogpu_v548_release_operations_handoff.ps1`, `tests/current/test_biogpu_v548_release_operations_handoff.py`, `docs/RELEASE_OPERATIONS_HANDOFF_GUIDE_V548.md` and `examples/biosdk_v548_release_operations_handoff.py`.
- v5.48 gate passed with `release_operations_handoff_contract_ready=true`, `v547_dependency_ready=true`, `release_operations_runbook_ready=true`, `operator_handoff_matrix_ready=true`, `operator_handoff_packet_ready=true`, `claim_boundary_attestation_ready=true`, `production_release_ready=false`, `production_operations_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.48. v5.48 explicitly answers that many proof layers still remain before production and OS readiness: real operator identities and approvals, production runbook signoff, live private registry administration, production token revocation/package yank authority, notification provider integration, support/incident systems, CI/CD gates, external acceptance records, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.49 Production readiness gap and staged pilot contract

- Implemented `biogpu/sdk/production_readiness_gap_v549.py`: local production readiness policy, 12-domain gap matrix, staged pilot acceptance matrix, local pilot acceptance plan, readiness blocker register and production-readiness audit bundle over the v5.48 release operations handoff contract.
- Added `biogpu/benchmarks/biogpu_v549_production_readiness_gap.py`, `scripts/run_biogpu_v549_production_readiness_gap.ps1`, `tests/current/test_biogpu_v549_production_readiness_gap.py`, `docs/PRODUCTION_READINESS_GAP_GUIDE_V549.md` and `examples/biosdk_v549_production_readiness_gap.py`.
- v5.49 gate passed with `production_readiness_gap_contract_ready=true`, `v548_dependency_ready=true`, `production_readiness_gap_matrix_ready=true`, `staged_pilot_acceptance_matrix_ready=true`, `staged_pilot_acceptance_plan_ready=true`, `readiness_blocker_register_ready=true`, `open_gap_count=12`, `production_ready_domain_count=0`, `production_ready=false`, `real_external_pilot_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.49. v5.49 remains a local readiness-gap proof only: real production identity, persistent tenant membership, production storage, hosted workers, live private registry, trusted signing, CI/CD gates, security signoff, support/incident systems, notification integration, external pilot acceptance, OS service supervision, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.50 External acceptance evidence and real-pilot intake contract

- Implemented `biogpu/sdk/external_acceptance_intake_v550.py`: local external acceptance intake policy, required evidence schema, evidence matrix, real-pilot intake gate, local acceptance packet, blocker register and audit bundle over the v5.49 production readiness gap contract.
- Added `biogpu/benchmarks/biogpu_v550_external_acceptance_intake.py`, `scripts/run_biogpu_v550_external_acceptance_intake.ps1`, `tests/current/test_biogpu_v550_external_acceptance_intake.py`, `docs/EXTERNAL_ACCEPTANCE_INTAKE_GUIDE_V550.md` and `examples/biosdk_v550_external_acceptance_intake.py`.
- v5.50 gate passed with `external_acceptance_intake_contract_ready=true`, `v549_dependency_ready=true`, `external_acceptance_evidence_schema_ready=true`, `external_acceptance_evidence_matrix_ready=true`, `real_pilot_intake_gate_ready=true`, `external_acceptance_packet_ready=true`, `real_pilot_intake_blocker_register_ready=true`, `required_evidence_type_count=10`, `schema_valid_record_count=10`, `real_acceptance_ready_count=0`, `accepted_local_intake_stage_count=3`, `denied_intake_gate_count=9`, `real_pilot_intake_blocker_count=19`, `real_external_pilot_ready=false`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.50. v5.50 remains a local external-acceptance intake proof only: real pilot partner identity records, signed data-use approvals, external security signoff, production identity-provider approval, live registry administrative approval, trusted signing authority approval, production CI/CD acceptance, support/incident acceptance, notification acceptance, rollback/yank acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.51 Partner data-room manifest and external review packet contract

- Implemented `biogpu/sdk/partner_dataroom_review_packet_v551.py`: local partner data-room policy, required manifest items, external review packet sections, review preflight gate, external-review blocker register and audit bundle over the v5.50 external acceptance intake contract.
- Added `biogpu/benchmarks/biogpu_v551_partner_dataroom_review_packet.py`, `scripts/run_biogpu_v551_partner_dataroom_review_packet.ps1`, `tests/current/test_biogpu_v551_partner_dataroom_review_packet.py`, `docs/PARTNER_DATAROOM_REVIEW_PACKET_GUIDE_V551.md` and `examples/biosdk_v551_partner_dataroom_review_packet.py`.
- v5.51 gate passed with `partner_dataroom_review_packet_contract_ready=true`, `v550_dependency_ready=true`, `partner_dataroom_manifest_ready=true`, `external_review_packet_ready=true`, `external_review_gate_ready=true`, `external_review_blocker_register_ready=true`, `required_dataroom_item_count=12`, `local_manifest_item_ready_count=12`, `real_dataroom_item_ready_count=0`, `external_review_packet_section_count=8`, `external_review_completed_count=0`, `accepted_local_review_stage_count=3`, `denied_external_review_gate_count=9`, `external_review_blocker_count=21`, `real_external_review_ready=false`, `real_external_pilot_ready=false`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.51. v5.51 remains a local data-room/review-packet proof only: real partner data-room workspace, external reviewer identities, reviewer access acknowledgements, signed packet acceptance, immutable review transcript, partner data-use approval, external security signoff, production IdP approval, live registry administration, trusted signing authority approval, production CI/CD/rollback acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.52 External reviewer questionnaire and signed response intake contract

- Implemented `biogpu/sdk/external_reviewer_response_intake_v552.py`: local external reviewer response policy, questionnaire scoring matrix, signed review-response packet shape, signed-response intake gate, blocker register and audit bundle over the v5.51 partner data-room review packet contract.
- Added `biogpu/benchmarks/biogpu_v552_external_reviewer_response_intake.py`, `scripts/run_biogpu_v552_external_reviewer_response_intake.ps1`, `tests/current/test_biogpu_v552_external_reviewer_response_intake.py`, `docs/EXTERNAL_REVIEWER_RESPONSE_INTAKE_GUIDE_V552.md` and `examples/biosdk_v552_external_reviewer_response_intake.py`.
- v5.52 gate passed with `external_reviewer_response_intake_contract_ready=true`, `v551_dependency_ready=true`, `questionnaire_scoring_matrix_ready=true`, `signed_review_response_packet_ready=true`, `signed_review_response_gate_ready=true`, `signed_response_blocker_register_ready=true`, `questionnaire_domain_count=10`, `local_questionnaire_score_ready_count=10`, `signed_review_response_ready_count=0`, `response_packet_record_count=10`, `external_review_completed_count=0`, `accepted_local_response_stage_count=3`, `denied_signed_response_gate_count=9`, `signed_response_blocker_count=19`, `real_signed_review_response_ready=false`, `real_external_review_ready=false`, `real_external_pilot_ready=false`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.52 with `371 passed`. v5.52 remains a local questionnaire-scoring and signed-response-intake proof only: real external reviewer identities, signed questionnaire responses, review session timestamps, immutable review transcript, signed response verification material, data-room access logs, reviewer finding disposition approvals, partner data-use approval, external security signoff, production IdP approval, live registry administration, trusted signing authority approval, production CI/CD/rollback acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.53 External review finding triage and remediation-plan contract

- Implemented `biogpu/sdk/external_review_finding_triage_v553.py`: local external review finding triage policy, finding triage matrix, remediation-plan packet shape, closure preflight gate, remediation blocker register and audit bundle over the v5.52 external reviewer response intake contract.
- Added `biogpu/benchmarks/biogpu_v553_external_review_finding_triage.py`, `scripts/run_biogpu_v553_external_review_finding_triage.ps1`, `tests/current/test_biogpu_v553_external_review_finding_triage.py`, `docs/EXTERNAL_REVIEW_FINDING_TRIAGE_GUIDE_V553.md` and `examples/biosdk_v553_external_review_finding_triage.py`.
- v5.53 gate passed with `external_review_finding_triage_contract_ready=true`, `v552_dependency_ready=true`, `review_finding_triage_matrix_ready=true`, `remediation_plan_packet_ready=true`, `remediation_closure_gate_ready=true`, `remediation_blocker_register_ready=true`, `review_finding_count=10`, `local_finding_triage_ready_count=10`, `local_remediation_plan_ready_count=10`, `real_remediation_approval_count=0`, `review_finding_closed_count=0`, `remediation_plan_record_count=10`, `accepted_local_triage_stage_count=3`, `denied_remediation_closure_gate_count=9`, `remediation_blocker_count=19`, `real_review_finding_closure_ready=false`, `real_external_review_ready=false`, `real_external_pilot_ready=false`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.53 with `379 passed`. v5.53 remains a local finding-triage and remediation-plan proof only: real external review finding register, external reviewer identities, signed finding dispositions, remediation owner approvals, closure signatures, finding closure timestamps, immutable review transcript, partner data-room access logs, partner data-use approval, external security signoff, production IdP approval, live registry administration, trusted signing authority approval, production CI/CD/rollback acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.54 Remediation evidence verification and closure attestation contract

- Implemented `biogpu/sdk/remediation_evidence_closure_v554.py`: local remediation evidence closure policy, remediation evidence verification matrix, closure attestation packet shape, closure-attestation preflight gate, closure attestation blocker register and audit bundle over the v5.53 external review finding triage contract.
- Added `biogpu/benchmarks/biogpu_v554_remediation_evidence_closure.py`, `scripts/run_biogpu_v554_remediation_evidence_closure.ps1`, `tests/current/test_biogpu_v554_remediation_evidence_closure.py`, `docs/REMEDIATION_EVIDENCE_CLOSURE_GUIDE_V554.md` and `examples/biosdk_v554_remediation_evidence_closure.py`.
- v5.54 gate passed with `remediation_evidence_closure_contract_ready=true`, `v553_dependency_ready=true`, `remediation_evidence_matrix_ready=true`, `closure_attestation_packet_ready=true`, `closure_attestation_gate_ready=true`, `closure_attestation_blocker_register_ready=true`, `remediation_evidence_record_count=10`, `local_remediation_evidence_verified_count=10`, `real_closure_attestation_ready_count=0`, `finding_closure_attested_count=0`, `closure_attestation_record_count=10`, `accepted_local_closure_stage_count=3`, `denied_closure_attestation_gate_count=9`, `closure_attestation_blocker_count=19`, `real_closure_attestation_ready=false`, `real_review_finding_closure_ready=false`, `real_external_review_ready=false`, `real_external_pilot_ready=false`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.54 with `387 passed`. v5.54 remains a local remediation evidence verification and closure attestation packet proof only: real remediation evidence payloads, external reviewer recheck records, remediation owner attestations, closure signatures/timestamps, immutable closure transcript, partner data-room access logs, partner data-use approval, external security signoff, production IdP approval, live registry administration, trusted signing authority approval, production CI/CD/rollback acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers.

### 2026-05-07 — v5.55 Closure attestation audit trail and external reviewer signoff registry contract

- Implemented `biogpu/sdk/closure_signoff_registry_v555.py`: local closure signoff registry policy, signoff registry matrix, closure signoff audit trail, external reviewer signoff packet shape, signoff-registry preflight gate, blocker register and audit bundle over the v5.54 remediation evidence closure contract.
- Added `biogpu/benchmarks/biogpu_v555_closure_signoff_registry.py`, `scripts/run_biogpu_v555_closure_signoff_registry.ps1`, `tests/current/test_biogpu_v555_closure_signoff_registry.py`, `docs/CLOSURE_SIGNOFF_REGISTRY_GUIDE_V555.md` and `examples/biosdk_v555_closure_signoff_registry.py`.
- v5.55 gate passed with `closure_signoff_registry_contract_ready=true`, `v554_dependency_ready=true`, `closure_signoff_registry_policy_ready=true`, `signoff_registry_matrix_ready=true`, `closure_signoff_audit_trail_ready=true`, `external_reviewer_signoff_packet_ready=true`, `signoff_registry_gate_ready=true`, `signoff_registry_blocker_register_ready=true`, `closure_signoff_registry_audit_bundle_ready=true`, `signoff_registry_record_count=10`, `local_signoff_registry_record_ready_count=10`, `local_audit_trail_ready_count=10`, `audit_event_count=80`, `signoff_packet_record_count=10`, `real_external_reviewer_signoff_ready_count=0`, `real_closure_signoff_ready_count=0`, `review_finding_closed_count=0`, `accepted_local_signoff_stage_count=3`, `denied_signoff_registry_gate_count=10`, `signoff_registry_blocker_count=20`, `production_distance=far`, `bic_os_distance=very_far`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.55 with `395 passed`. v5.55 remains a local closure attestation audit trail and external reviewer signoff registry proof only: real external reviewer identity records, external reviewer recheck records, signed reviewer signoff manifests, immutable closure transcripts, signed closure timestamps, real partner data-room access logs, partner data-use approval, external security signoff, production IdP approval, live registry administration, trusted signing authority approval, production CI/CD/rollback acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers. Production is still far; BiC OS is still very far and remains locked behind full BioSDK, production BioCompute Runtime, NSI/control-plane maturity and real-world validation.

### 2026-05-07 — v5.56 External signoff intake and signed closure transcript acceptance contract

- Implemented `biogpu/sdk/external_signoff_transcript_intake_v556.py`: local intake policy for real external reviewer signoff payloads, external signoff intake matrix, signed closure transcript packet shape, transcript acceptance gate, blocker register and audit bundle over the v5.55 closure signoff registry contract.
- Added `biogpu/benchmarks/biogpu_v556_external_signoff_transcript_intake.py`, `scripts/run_biogpu_v556_external_signoff_transcript_intake.ps1`, `tests/current/test_biogpu_v556_external_signoff_transcript_intake.py`, `docs/EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_GUIDE_V556.md` and `examples/biosdk_v556_external_signoff_transcript_intake.py`.
- v5.56 gate passed with `external_signoff_transcript_intake_contract_ready=true`, `v555_dependency_ready=true`, `external_signoff_transcript_intake_policy_ready=true`, `external_signoff_intake_matrix_ready=true`, `signed_closure_transcript_packet_ready=true`, `transcript_acceptance_gate_ready=true`, `transcript_acceptance_blocker_register_ready=true`, `external_signoff_transcript_intake_audit_bundle_ready=true`, `signoff_intake_record_count=10`, `local_signoff_intake_record_ready_count=10`, `local_transcript_reference_ready_count=10`, `transcript_packet_section_count=8`, `local_transcript_packet_section_ready_count=8`, `real_external_signoff_accepted_count=0`, `signed_closure_transcript_accepted_count=0`, `review_finding_closed_count=0`, `accepted_local_intake_stage_count=3`, `denied_transcript_acceptance_gate_count=10`, `transcript_acceptance_blocker_count=20`, `production_distance=far`, `bic_os_distance=very_far`, `production_ready=false`, `full_biosdk_ready=false` and `bic_os_phase_locked=true`.
- Full `tests/current` regression passed after v5.56 with `403 passed`. v5.56 remains a local intake and signed-transcript acceptance-gate proof only: real external reviewer identity evidence, reviewer authorization evidence, reviewer recheck evidence, signed external reviewer signoff manifest, signed closure transcript, closure timestamp evidence, owner counter-attestation, immutable transcript anchor, real finding closure crosswalk, partner data-room access logs, partner data-use approval, external security signoff, production IdP approval, live registry administration, trusted signing authority approval, production CI/CD/rollback acceptance, full BioSDK, production BioCompute Runtime and BiC OS readiness remain blockers. Production is still far; BiC OS is still very far and remains locked behind full BioSDK, production BioCompute Runtime, NSI/control-plane maturity and real-world validation.

### 2026-05-06 — v5.0 active development start

- v4.3 standalone workspace was consolidated into the v5.0 legacy archive for reference-only recovery.
- v5.0 is now the single active project root.
- Added Windows PowerShell runners for PC validation smoke and compact replay checks.
- Smoke validation passed: `pip check`, `compileall`, current tests, v47 final PC patch, and v50 differentiation report.
- Fast Windows compact replay pass completed for v33 and v36 using centroid/diagonal decoders.
- Full `Pre_processed_MEA_data.zip` checksum validation passed after placing the official archive at `data/external/Pre_processed_MEA_data.zip`.
- Data gate status is now `zip_checksum_validated` for the Zenodo 14363732 preprocessed MEA asset.
- Full lineage-strict `full_shuffle_1000` completed on Windows using centroid/diagonal decoders: 24 sweep rows, 24,000 shuffled-control rows, 2,000 bootstrap iterations, best balanced accuracy 0.929974, empirical p-value 0.000999, and result bundle SHA256 `951C084E7A41AB6846D32547E78292257E0E5B79EA3AAA2BD013837AF7616891`.
- PC validation phase now has smoke, compact, ZIP checksum, full-shuffle controls, bootstrap CI summaries, and a reproducible v36 lineage evidence bundle.
- Added v5.0 PC validation bundle packaging without embedding the full dataset archive.
- Extended-methods Core profile completed on Windows: 10 lineage-strict split offsets, 40 sweep rows, 200,000 shuffled-control rows, 5,000 bootstrap iterations, best balanced accuracy 0.929974, empirical p-value 0.000200, and result bundle SHA256 `D2E7CD2FA137F45EE8AA8B3C9A0F9DA76A59F114EAF5698CD963C6702F948911`.
- Rebuilt the v5.0 PC validation bundle with extended-methods artifacts included: 41 artifacts. Current bundle size and SHA256 are recorded in `outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json`, not duplicated here because this plan file is included in the bundle.

### 2026-05-06 — v5.1 Dataset/API expansion phase start

- Dataset/API expansion phase initiated.
- Implemented `biogpu/data_ingest/zenodo_raw_hdf5_gate.py`: offline gate for Zenodo 14363732 raw HDF5 / TTL assets; returns `not_downloaded` when raw HDF5 files are absent, `available` when present, with download hints for both asset groups. No network calls at any point.
- Implemented `biogpu/benchmarks/biogpu_v51_dataset_api_expansion.py`: full probe runner covering all six Dataset/API expansion sources (raw HDF5 gate, DANDI candidate manifest, DANDI/NWB offline gate, synthetic orientation dataset, vendor registry v4.2, user-upload importer skeleton v4.2). Writes `V51_DATASET_EXPANSION_SUMMARY.json` under `outputs/v51_dataset_expansion/`.
- Added `scripts/run_biogpu_v51_dataset_api_expansion.ps1`: Windows runner that executes the probe and then runs the new v51 tests.
- Added 23 new tests in `tests/current/test_biogpu_v51_dataset_api_expansion.py` covering all six probes and offline gate logic.
- Current pytest count: **48 passed** (was 25 before v5.0 bundle tests, 48 after v5.1 dataset expansion tests).
- Gate status as of this date: `raw_hdf5=not_downloaded`, `nwb=not_downloaded`, `orientation_synthetic=available`, `vendor_registry=loaded`. Raw HDF5 and NWB files can be downloaded independently from Zenodo 14363732 and DANDI 000469 respectively to unlock the next level of dataset expansion.

### 2026-05-06 — v5.2 NSI/interface phase start

- NSI/interface phase initiated while the large Zenodo raw HDF5 archive downloads in a resumable background terminal.
- Upgraded `biogpu/standards/nsi_v10.py` from a draft list into the frozen NSI-1.0 runtime-facing profile: seven JSON-schema-like core objects, safety modes, claim levels, reference objects, object validation, result-bundle validation, and conservative claim-level annotation.
- Added `biogpu/standards/nsi_conformance_v52.py`: adapter conformance helpers for all dataset importer skeletons and safe dry-run vendor adapters.
- Added `biogpu/benchmarks/biogpu_v52_nsi_interface.py`: v5.2 runner that writes frozen schema artifacts, reference object validation, dataset/vendor conformance reports, result-bundle validation, and `V52_NSI_INTERFACE_SUMMARY.json` under `outputs/v52_nsi_interface/`.
- Added `scripts/run_biogpu_v52_nsi_interface.ps1`: Windows runner for the v5.2 NSI/interface gate.
- Added `docs/NSI_1_0_ADAPTER_GUIDE_V52.md`: developer guide for adapter contracts, safety profiles, result bundles, claim levels, and local conformance.
- Added 9 new tests in `tests/current/test_biogpu_v52_nsi_interface.py` covering schema freeze, reference validation, safety/write blocking, result-bundle validation, claim annotation, adapter conformance, and runner output.
- v5.2 gate passed: 7 schemas frozen, 7/7 dataset importers conform, 4/4 vendor adapter stubs conform, reference result bundle validates.
- Current pytest count after the initial NSI/interface gate: **57 passed** across `tests/current`.
- Added public `validate-nsi` CLI wrapper: `biogpu-validate-nsi`, `python -m biogpu.standards.nsi_cli_v52`, and `python -m biogpu.cli validate-nsi` can list schemas, validate NSI JSON payloads, write validation reports, and generate local reference objects.
- Added 6 CLI tests in `tests/current/test_biogpu_v52_validate_nsi_cli.py` covering schema listing, valid/invalid payload validation, report writing, reference object generation, and the existing `biogpu.cli` subcommand.
- Current pytest count after the validate-nsi CLI wrapper: **63 passed** across `tests/current`.

### 2026-05-06 — v5.3 Evidence Ledger phase start

- Evidence Ledger phase initiated while the Zenodo raw HDF5 archive continues downloading in the background.
- Added `biogpu/evidence/ledger_v53.py`: ZIP evidence bundle validator, manifest-aware v50/v24 bundle checks, artifact SHA256/size verification, unsafe ZIP member rejection, chained ledger entries, chain-root validation, and local HMAC integrity signatures.
- Added `biogpu/benchmarks/biogpu_v53_evidence_ledger.py`: runner that creates a reference v24 result bundle, audits available evidence bundles including the v5.0 PC validation bundle when present, writes `V53_EVIDENCE_LEDGER.json`, chain validation, bundle reports, and summary under `outputs/v53_evidence_ledger/`.
- Added `scripts/run_biogpu_v53_evidence_ledger.ps1`: Windows gate for v5.3 evidence ledger validation and focused tests.
- Added 6 tests in `tests/current/test_biogpu_v53_evidence_ledger.py` covering valid v50-like bundle validation, checksum mismatch detection, unsafe ZIP path rejection, ledger chain validation, local signature determinism, and runner output.
- v5.3 gate passed: 2 audited bundles, 2 valid bundles, ledger chain valid, reference bundle valid.
- Current pytest count after v5.3 evidence ledger: **69 passed** across `tests/current`.

### 2026-05-06 — v5.4 LLM/Agent Bridge phase start

- LLM/Agent Bridge phase initiated on top of NSI-1.0 and the v5.3 Evidence Ledger discipline.
- Added `biogpu/llm/agent_bridge_v54.py`: structured tool catalog, `BioComputeAgentRequestV54`, policy review, forbidden live-lab payload scanning, blocked-by-default operation checks, approval-aware live-shadow gating, claim annotation, and safe conversion into NSI `BioComputeTaskManifest` objects.
- Added `biogpu/benchmarks/biogpu_v54_llm_agent_bridge.py`: runner that writes the v5.4 tool catalog, reference agent requests, policy responses, summary and report under `outputs/v54_llm_agent_bridge/`.
- Added `scripts/run_biogpu_v54_llm_agent_bridge.ps1`: Windows gate for the v5.4 probe and focused tests.
- Added `docs/LLM_AGENT_BRIDGE_GUIDE_V54.md`: developer guide for the bridge request flow, tool catalog, safety boundary, outputs and validation command.
- Added 10 tests in `tests/current/test_biogpu_v54_llm_agent_bridge.py` covering catalog shape, safe replay manifest emission, forbidden live fields, direct actuation blocking, live-shadow approval gating, claim downgrade for unapproved live-shadow, protocol-only approval rejection, unknown tools and runner output.
- v5.4 gate passed: 8 structured BioCompute agent tools, safe replay approved, approval-backed live-shadow approved as read-only, direct actuation blocked, and NSI manifests emitted only for approved requests.
- Current pytest count after v5.4 LLM/Agent Bridge: **79 passed** across `tests/current`.

### 2026-05-06 — v5.5 Control Plane Queue Bridge phase start

- Hosted/private beta phase initiated offline while the Zenodo raw HDF5 archive continues downloading.
- Added `biogpu/beta/control_plane_v55.py`: compatibility bridge from approved v5.4 agent responses into the existing v4.3 hosted job model, including tool-to-job mapping, NSI manifest validation, live-shadow tier gating and blocked-actuation rejection.
- Added `biogpu/benchmarks/biogpu_v55_control_plane_queue.py`: runner that writes the queue demo, summary and report under `outputs/v55_control_plane_queue/`.
- Added `scripts/run_biogpu_v55_control_plane_queue.ps1`: Windows gate for the v5.5 queue bridge probe and focused tests.
- Added `docs/CONTROL_PLANE_QUEUE_GUIDE_V55.md`: developer guide for the v5.4 agent response to v4.3 hosted queue admission flow.
- Added 7 tests in `tests/current/test_biogpu_v55_control_plane_queue.py` covering safe replay queue admission, blocked agent denial, unapproved live-shadow denial, live-shadow tier gating, viewer role rejection through the v4.3 job validator, reference demo safety outcomes and runner output.
- v5.5 gate passed: safe replay queued, enterprise live-shadow queued as read-only/API validation, developer live-shadow rejected, blocked actuation rejected, and no live actuation enabled.
- Current pytest count after v5.5 Control Plane Queue Bridge: **86 passed** across `tests/current`.

### 2026-05-06 — Zenodo raw HDF5 archive download completed

- `data/external/Raw_data_MEA_data.zip` download completed with matching MD5: `189bf2fc0ce858fd1308d683e1e8c323`.
- Archive extracted into `data/external/raw_hdf5/`.
- v5.1 raw HDF5 gate now reports HDF5 files as available (`42` `.h5` files, ~33.58 GB extracted) and TTL CSV files as missing (`0` `.csv`), so overall status is `partial`.
- Updated v5.1 summary-note generation to report actual gate statuses (`raw_hdf5` and `dandi_nwb`) instead of a static `not_downloaded` note.

### 2026-05-06 — v5.6 Raw HDF5 structure/event inspection phase start

- Raw HDF5/TTL reconstruction phase initiated on the extracted Zenodo raw archive.
- Added `biogpu/data_ingest/zenodo_raw_hdf5_v56.py`: safe MCS HDF5 RawData structure inspector that maps protocol metadata, analog stream paths, channel/sample counts, inferred sample rate, embedded EventStream entities, detector kind, target IDs and stimulation-kind counts without loading full waveform matrices into memory.
- Added `biogpu/benchmarks/biogpu_v56_raw_hdf5_structure.py`: runner that writes raw structure summary, full file report, TTL/event candidates CSV, raw stimulus-window preview CSV and markdown report under `outputs/v56_raw_hdf5_structure/`.
- Added `scripts/run_biogpu_v56_raw_hdf5_structure.ps1`: Windows gate for raw HDF5 structure/event inspection and focused tests.
- Added `docs/RAW_HDF5_STRUCTURE_GUIDE_V56.md`: guide for the raw HDF5 inspection outputs and safety boundary.
- Added 5 tests in `tests/current/test_biogpu_v56_raw_hdf5_structure.py` using a small synthetic MCS-style HDF5 fixture.
- v5.6 gate passed on real extracted raw data: 42 HDF5 files inspected, 42 valid files, 22 files with embedded events, 44 event candidate datasets, 5,946 event timestamps, 33.584 GB extracted HDF5, 0 external TTL CSV files.
- Current pytest count after v5.6 Raw HDF5 structure/event inspection: **91 passed** across `tests/current`.

### 2026-05-06 — v5.7 Raw-vs-preprocessed alignment audit phase start

- Added `biogpu/data_ingest/raw_preprocessed_alignment_v57.py`: audit layer that groups v5.6 raw EventStream candidates and v15 pulse metadata by date, culture, condition, target and recording stem.
- Added `biogpu/benchmarks/biogpu_v57_raw_preprocessed_alignment.py`: runner that writes raw event recordings, preprocessed pulse recordings, alignment audit CSV, summary JSON and markdown report under `outputs/v57_raw_preprocessed_alignment/`.
- Added `scripts/run_biogpu_v57_raw_preprocessed_alignment.ps1`: Windows gate for the raw-vs-preprocessed audit and focused tests.
- Added `docs/RAW_PREPROCESSED_ALIGNMENT_GUIDE_V57.md`: guide for exact-overlap, condition/target and temporal-signature statuses.
- Added 6 focused tests in `tests/current/test_biogpu_v57_raw_preprocessed_alignment.py` covering raw grouping, pulse grouping, exact alignment, target/temporal-only alignment, temporal-only alignment, missing inputs and runner outputs.
- v5.7 gate passed on real artifacts: 22 raw event recordings from v5.6, 41 preprocessed pulse recordings from v15, 0 exact recording matches, 0 date/culture/target matches, 3 condition/target matches, 19 temporal-signature matches, 1 date/culture overlap and shared LightStim targets 34, 55 and 67.
- Interpretation: raw HDF5 EventStream evidence supports event/cadence understanding but does not yet prove raw-to-feature reconstruction for the v15/v50 PC validation rows because exact recording overlap is absent in the current local subsets.
- Current pytest count after v5.7 Raw-vs-preprocessed alignment audit: **97 passed** across `tests/current`.

### 2026-05-06 — v5.8 Raw-native HDF5 benchmark phase start

- Added `biogpu/data_ingest/raw_native_benchmark_v58.py`: raw-native HDF5 EventStream feature extractor that reads only small analog `ChannelData` windows around selected raw event timestamps. It handles variable channel counts by padding feature vectors to a common width while preserving original channel counts in metadata.
- Added `biogpu/benchmarks/biogpu_v58_raw_native_benchmark.py`: runner that writes raw-native feature matrix NPZ, event metadata CSV, source CSV, condition readout JSON, summary JSON and markdown report under `outputs/v58_raw_native_benchmark/`.
- Added `scripts/run_biogpu_v58_raw_native_benchmark.ps1`: Windows gate for real raw-native extraction and focused synthetic HDF5 tests.
- Added `docs/RAW_NATIVE_BENCHMARK_GUIDE_V58.md`: guide for raw-native feature extraction, outputs, readout and claim boundary.
- Added 5 focused tests in `tests/current/test_biogpu_v58_raw_native_benchmark.py` covering primary EventStream source selection, HDF5 window slicing, missing-file handling, group-heldout condition readout and runner outputs.
- v5.8 gate passed on real raw HDF5 data: 22 raw event sources, 352 raw event-window feature rows, 236 padded features, 22 recordings with features, 0 skipped events, 0 skipped sources and 0 read errors.
- v5.8 group-heldout condition readout completed: observed accuracy 0.4545, observed balanced accuracy 0.6667, shuffle median balanced accuracy 0.5 and p-value 0.1154 over 25 label shuffles. This is an exploratory raw-native signal, not a strong performance claim.
- Current pytest count after v5.8 Raw-native HDF5 benchmark: **102 passed** across `tests/current`.

### 2026-05-06 — v5.9 Raw-native stability and target coverage audit phase start

- Added `biogpu/analysis/raw_native_stability_v59.py`: loads v5.8 raw-native feature matrix/metadata, computes target eligibility, within-recording split-half repeatability, group-heldout target readout and repeated-target fingerprint similarity.
- Added `biogpu/benchmarks/biogpu_v59_raw_native_stability_audit.py`: runner for v5.9 summary JSON, target eligibility CSV, split-half JSON/CSV, target readout JSON, target fingerprint JSON and markdown report under `outputs/v59_raw_native_stability_audit/`.
- Added `scripts/run_biogpu_v59_raw_native_stability_audit.ps1`: Windows gate using existing v5.8 outputs, with 200 label shuffles by default.
- Added `docs/RAW_NATIVE_STABILITY_AUDIT_GUIDE_V59.md`: explains repeatability, repeated-target eligibility, target audit outputs and claim boundary.
- Added 6 focused tests in `tests/current/test_biogpu_v59_raw_native_stability_audit.py` covering v5.8-like loading, target eligibility, split-half repeatability, separable synthetic target readout/fingerprint, insufficient repeated targets and runner outputs.
- v5.9 gate passed on real v5.8 raw-native artifacts: 352 feature rows, 236 features, 22 recording groups and 18 target labels.
- v5.9 repeatability result: within-recording split-half cosine median 0.99998, cross-recording centroid cosine median 0.57509 and median margin 0.42489. This supports stable raw event-window feature extraction within recordings.
- v5.9 target audit result: only 3 repeated target labels are eligible (`elecstim:44`, `elecstim:52`, `elecstim:62`); group-heldout target readout balanced accuracy 0.3889 with p=0.4378, and target fingerprint margin 0.0022 with p=0.2935. Target-ID signal is **not supported** on the current sparse repeated-target raw subset.
- Current pytest count after v5.9 Raw-native stability audit: **108 passed** across `tests/current`.

### 2026-05-06 — v5.10 Project alignment and claim audit phase start

- Added `biogpu/claims/project_alignment_v510.py`: project-level claim register and direct-answer audit over local v50-v59 artifacts.
- Added `biogpu/benchmarks/biogpu_v510_project_alignment_claim_audit.py`: runner that writes project alignment summary, claim register JSON/CSV and markdown report under `outputs/v510_project_alignment_claim_audit/`.
- Added `scripts/run_biogpu_v510_project_alignment_claim_audit.ps1`: Windows gate for the v5.10 audit and focused tests.
- Added `docs/PROJECT_ALIGNMENT_CLAIM_AUDIT_GUIDE_V510.md`: guide explaining that local artifacts can prove alignment and claim discipline but cannot prove global uniqueness.
- Added 5 focused tests in `tests/current/test_biogpu_v510_project_alignment_claim_audit.py` covering claim register status, direct answer, missing-artifact partial alignment, output writing and runner output.
- v5.10 gate passed on real project artifacts with status `on_mission_with_claim_boundaries`.
- Direct answer recorded: project drift = `no`; global uniqueness = `no_local_tests_cannot_prove_global_uniqueness`.
- v5.10 supports local code distinctness/integrated architecture, vendor-neutral standard direction, raw-native feature matrix and raw-native repeatability. It explicitly blocks or rejects global uniqueness proof, first biological computer, live BioGPU proof, GPU replacement/energy superiority, production OS, v15/v50 raw equivalence and current raw target-ID decoding.
- Current pytest count after v5.10 Project alignment and claim audit: **113 passed** across `tests/current`.

### 2026-05-06 — v5.11 BiC OS boot readiness phase start

- Added `biogpu/os/boot_readiness_v511.py`: BiC OS subsystem readiness model and offline runtime-kernel boot audit over v5.2-v5.10 artifacts.
- Added `biogpu/benchmarks/biogpu_v511_bic_os_boot_readiness.py`: runner that writes boot readiness summary, boot manifest, subsystem CSV and markdown report under `outputs/v511_bic_os_boot_readiness/`.
- Added `scripts/run_biogpu_v511_bic_os_boot_readiness.ps1`: Windows gate for v5.11 boot readiness and focused tests.
- Added `docs/BIC_OS_BOOT_READINESS_GUIDE_V511.md`: guide explaining what boots now and what still blocks a full OS.
- Added 5 focused tests in `tests/current/test_biogpu_v511_bic_os_boot_readiness.py` covering offline boot readiness, missing-artifact failure, production blockers, output writing and runner output.
- v5.11 expected healthy status: `bic_os_offline_runtime_kernel_boot_ready_production_os_not_claimed`.
- v5.11 gate passed on real project artifacts: `product_name=BiC OS`, `offline_runtime_kernel_bootable=True`, `production_os_ready=False` and `production_blocker_count=5`.
- v5.11 production blockers are scheduler/worker daemon, permission/identity system, adapter plugin manager, dashboard control plane and live telemetry/lab gateway.
- v5.11 keeps the name `BiC OS` explicit while preserving the claim boundary: offline runtime kernel can be audited; production OS, global uniqueness, live BioGPU proof, GPU replacement and energy superiority cannot yet be claimed.
- Current pytest count after v5.11 BiC OS boot readiness: **118 passed** across `tests/current`.

### 2026-05-06 — v5.12 BioSDK evidence pack phase start

- Added `biogpu/sdk/evidence_pack_v512.py`: BioSDK capability matrix and evidence-kernel readiness audit over v5.0-v5.11 artifacts.
- Added `biogpu/benchmarks/biogpu_v512_biosdk_evidence_pack.py`: runner that writes BioSDK evidence summary, capability matrix JSON/CSV and markdown report under `outputs/v512_biosdk_evidence_pack/`.
- Added `scripts/run_biogpu_v512_biosdk_evidence_pack.ps1`: Windows gate for the v5.12 BioSDK proof layer and focused tests.
- Added `docs/BIOSDK_EVIDENCE_PACK_GUIDE_V512.md`: guide explaining why BioSDK proof must precede full BiC OS claims and what makes the project a useful working tool.
- Added 5 focused tests in `tests/current/test_biogpu_v512_biosdk_evidence_pack.py` covering evidence-kernel readiness, usefulness/uniqueness thesis, missing-artifact failure, output writing and runner output.
- v5.12 expected healthy status: `biosdk_evidence_kernel_ready_full_sdk_not_claimed`.
- v5.12 gate passed on real project artifacts: `biosdk_evidence_kernel_ready=True`, `full_biosdk_ready=False` and locally proven capabilities `8/9`.
- v5.12 capability gaps are dataset/API external validation, durable scheduler, raw equivalence/target-ID limits and production BiC OS bridge blockers.
- v5.12 preserves the core strategic rule: BiC OS should be reached by first proving the BioSDK and BioCompute Runtime through repeatable evidence gates.
- Current pytest count after v5.12 BioSDK evidence pack: **123 passed** across `tests/current`.

### 2026-05-06 — v5.13 BioSDK core API phase correction

- Added `biogpu/sdk/core_v513.py`: public BioSDK facade over v5.2 NSI validation, v5.4 agent review, v5.5 queue admission and v5.12 evidence pack.
- Added `biogpu/benchmarks/biogpu_v513_biosdk_core_api.py`: runner that writes SDK core summary, phase gate, reference flow and markdown report under `outputs/v513_biosdk_core_api/`.
- Added `examples/biosdk_v513_minimal_flow.py`: first minimal public SDK example for safe replay flow.
- Added `scripts/run_biogpu_v513_biosdk_core_api.ps1`: Windows gate for the v5.13 SDK facade and focused tests.
- Added `docs/BIOSDK_CORE_API_GUIDE_V513.md`: guide that makes BioSDK public core the active phase and keeps BiC OS locked.
- Added 6 focused tests in `tests/current/test_biogpu_v513_biosdk_core_api.py` covering phase lock, valid replay manifest, queue admission, unsafe actuation blocking, output writing and runner output.
- v5.13 expected healthy status: `biosdk_core_api_active_bic_os_locked`.
- v5.13 is a course correction: the project should not build new BiC OS layers until public SDK examples, external data/API validation, durable scheduler and installable SDK release gates are complete.

### 2026-05-06 — v5.14 BioSDK sample acquisition gate

- Added `biogpu/sdk/sample_acquisition_v514.py`: SDK-level sample requirement matrix over Zenodo preprocessed, Zenodo raw HDF5, DANDI/NWB, Allen orientation, external read-only API/export and vendor/user-upload samples.
- Added `biogpu/benchmarks/biogpu_v514_sample_acquisition_gate.py`: runner that writes sample acquisition summary, requirement matrix, download manifest and markdown report under `outputs/v514_sample_acquisition_gate/`.
- Added `scripts/download_dandi_nwb_sample_v514.ps1`: selective DANDI metadata query and capped one-file NWB downloader with `-PlanOnly` support.
- Added `scripts/run_biogpu_v514_sample_acquisition_gate.ps1`: Windows gate for v5.14 sample acquisition and focused tests.
- Added `examples/biosdk_v514_sample_inventory.py`: minimal SDK sample inventory example.
- Added `docs/SAMPLE_ACQUISITION_GUIDE_V514.md`: guide for capped sample downloads and proof boundaries.
- Added 5 focused tests in `tests/current/test_biogpu_v514_sample_acquisition_gate.py` covering local sample status, DANDI NWB unit detection, capped download manifest, output writing and runner output.
- v5.14 expected honest status before NWB/API downloads: `sample_proof_gate_ready_for_external_downloads`.
- v5.14 keeps BiC OS locked and makes the next data work explicit: DANDI NWB sample, external read-only API/export, Allen or vendor/user-upload samples, then SDK examples.

### 2026-05-06 — v5.15 DANDI/NWB task validation gate

- Downloaded one capped DANDI 000469 NWB sample: `data/external/nwb/dandi_000469/sub-20_ses-2_ecephys+image.nwb`, 25,582,000 bytes.
- Added `biogpu/sdk/nwb_task_validation_v515.py`: local NWB sample finder, units inspection, stimulus/trials discovery, interval label selection and task-window export.
- Added `biogpu/benchmarks/biogpu_v515_dandi_nwb_task_validation.py`: runner that writes summary, detailed sample reports, task-window CSV and markdown report under `outputs/v515_dandi_nwb_task_validation/`.
- Added `scripts/run_biogpu_v515_dandi_nwb_task_validation.ps1`: Windows gate for real DANDI/NWB task validation and focused tests.
- Added `docs/DANDI_NWB_TASK_VALIDATION_GUIDE_V515.md`: guide for the first external public-data parser proof.
- Added 5 focused tests in `tests/current/test_biogpu_v515_dandi_nwb_task_validation.py` covering sample discovery, units/trials/window validation, missing-sample gate, output writing and runner output.
- v5.15 expected healthy status with the downloaded sample: `dandi_nwb_task_sample_validated`.
- This advances the Dataset/API proof path but still does not satisfy external read-only API/export validation, Allen orientation validation, vendor/user-upload portability or full BioSDK release readiness.

### 2026-05-06 — v5.16 DANDI/NWB SDK task benchmark

- Added `biogpu/sdk/nwb_task_benchmark_v516.py`: feature extraction from validated NWB task windows using per-unit spike counts and firing rates, plus stratified nearest-centroid readout with shuffled-label baseline.
- Added `biogpu/benchmarks/biogpu_v516_dandi_nwb_task_benchmark.py`: runner that writes summary, feature matrix NPZ, trial feature CSV, readout JSON and markdown report under `outputs/v516_dandi_nwb_task_benchmark/`.
- Added `scripts/run_biogpu_v516_dandi_nwb_task_benchmark.ps1`: Windows gate for the v5.16 public DANDI/NWB SDK benchmark and focused tests.
- Added `examples/biosdk_v516_dandi_task_benchmark.py`: minimal SDK benchmark example.
- Added `docs/DANDI_NWB_TASK_BENCHMARK_GUIDE_V516.md`: guide for the public DANDI/NWB SDK benchmark and claim boundary.
- Added 5 focused tests in `tests/current/test_biogpu_v516_dandi_nwb_task_benchmark.py` covering feature extraction, stratified readout, missing-sample gate, output writing and runner output.
- v5.16 expected healthy status with the downloaded sample: `dandi_nwb_sdk_task_benchmark_available`.
- v5.16 remains exploratory single-sample evidence. External read-only API/export validation, Allen/vendor/user-upload samples, durable scheduler/workers and installable SDK release remain required.

### 2026-05-06 — v5.17 external read-only API/export contract gate

- Added `biogpu/sdk/external_readonly_v517.py`: SDK-level external read-only API gate over the v3.7 mock clients for FinalSpark, 3Brain, Axion and MCS.
- Added `biogpu/benchmarks/biogpu_v517_external_readonly_api_gate.py`: runner that writes summary, platform reports, trace fixtures and markdown report under `outputs/v517_external_readonly_api_gate/`.
- Added `scripts/run_biogpu_v517_external_readonly_api_gate.ps1`: Windows gate for external read-only adapter contract validation and focused tests.
- Added `examples/biosdk_v517_external_readonly_gate.py`: minimal SDK example for the external read-only gate.
- Added `docs/EXTERNAL_READONLY_API_GATE_GUIDE_V517.md`: guide explaining local mock contract proof vs real external API/export proof.
- Added 5 focused tests in `tests/current/test_biogpu_v517_external_readonly_api_gate.py` covering FinalSpark mock trace export, all-platform contract pass, non-secret export detection, output writing and runner output.
- v5.17 expected honest status without partner material: `mock_readonly_contract_passed_real_external_required`.
- v5.17 does not close the external API proof blocker. It proves read-only contract behavior and write denial locally; a real partner token/export is still required before stronger SDK/runtime claims.

### 2026-05-06 — v5.18 Allen visual-coding orientation intake gate

- Added `biogpu/sdk/allen_orientation_v518.py`: SDK-level Allen visual-coding orientation gate that scans `data/external/allen/`, inspects local NWB units/stimulus metadata when present, and keeps full Allen proof blocked until a real sample is available.
- Added `biogpu/benchmarks/biogpu_v518_allen_orientation_gate.py`: runner that writes summary, sample reports, asset manifest, download plan and markdown report under `outputs/v518_allen_orientation_gate/`.
- Added `scripts/run_biogpu_v518_allen_orientation_gate.ps1`: Windows gate for Allen orientation intake and focused tests.
- Added `examples/biosdk_v518_allen_orientation_gate.py` and `docs/ALLEN_ORIENTATION_GATE_GUIDE_V518.md`.
- Added 5 focused tests in `tests/current/test_biogpu_v518_allen_orientation_gate.py` covering missing-sample honesty, manifest detection, orientation signal discovery, output writing and runner output.
- v5.18 expected honest status without local Allen material: `allen_orientation_sample_missing_download_required`.
- v5.18 does not close the Allen proof blocker. It creates the validation path and download discipline for a small Allen sample.

### 2026-05-06 — v5.19 vendor/user-upload read-only intake gate

- Added `biogpu/sdk/vendor_upload_v519.py`: SDK-level scanner for `data/external/vendor_exports/` and `data/external/user_upload_samples/` with SHA256, extension/schema hints, v4.2 importer routing and forbidden live-field detection.
- Added `biogpu/benchmarks/biogpu_v519_vendor_user_upload_gate.py`: runner that writes summary, sample reports, CSV report, intake template and markdown report under `outputs/v519_vendor_user_upload_gate/`.
- Added `scripts/run_biogpu_v519_vendor_user_upload_gate.ps1`: Windows gate for vendor/user-upload intake and focused tests.
- Added `examples/biosdk_v519_vendor_user_upload_gate.py` and `docs/VENDOR_USER_UPLOAD_GATE_GUIDE_V519.md`.
- Added 5 focused tests in `tests/current/test_biogpu_v519_vendor_user_upload_gate.py` covering missing-sample honesty, safe user JSON validation, forbidden live-field blocking, vendor HDF5 routing and runner output.
- v5.19 expected honest status without local samples: `vendor_user_upload_sample_missing_required`.
- v5.19 does not close vendor/private upload proof without real safe read-only sample exports.

### 2026-05-06 — v5.20 Allen visual-coding orientation benchmark

- Downloaded a capped Allen Institute Visual Coding session NWB from DANDI `000021`: `sub-707296975_ses-721123822.nwb`, 1,736,516,600 bytes, selected because per-probe 68 MB LFP files did not contain `/units` and orientation tables.
- Added `scripts/download_allen_visual_coding_nwb_v518.ps1`: DANDI `000021` helper that prefers session-level NWB assets and avoids full Allen cache download.
- Added `biogpu/sdk/allen_orientation_benchmark_v520.py`: bounded top-unit feature extraction from `drifting_gratings_presentations` with orientation labels and shuffled-label controls.
- Added `biogpu/benchmarks/biogpu_v520_allen_orientation_benchmark.py`, `scripts/run_biogpu_v520_allen_orientation_benchmark.ps1`, `docs/ALLEN_ORIENTATION_BENCHMARK_GUIDE_V520.md` and 5 focused tests.
- v5.20 strengthens BioSDK evidence with a second independent public neurophysiology dataset, while external API/export and vendor/user-upload proof remain incomplete.

### 2026-05-06 — v5.21 cross-dataset BioSDK evidence pack

- Added `biogpu/sdk/cross_dataset_evidence_v521.py`: one proof matrix across Zenodo raw HDF5, DANDI NWB, Allen visual coding, external read-only API/export and vendor/user-upload intake.
- Added `biogpu/benchmarks/biogpu_v521_cross_dataset_evidence_pack.py`, `scripts/run_biogpu_v521_cross_dataset_evidence_pack.ps1`, `docs/CROSS_DATASET_EVIDENCE_PACK_GUIDE_V521.md` and 5 focused tests.
- v5.21 explicitly separates public cross-dataset evidence readiness from full BioSDK readiness: external real export/token and vendor/user sample remain blockers.

### 2026-05-06 — v5.22 BioSDK public examples gate

- Added `biogpu/sdk/public_examples_v522.py`: validates public SDK examples, emits an example catalog and runbook, and keeps external/vendor examples blocked until real material exists.
- Added `examples/biosdk_v520_allen_orientation_benchmark.py`, `examples/biosdk_v521_cross_dataset_evidence.py`, and `examples/biosdk_v522_public_examples.py`.
- Added `biogpu/benchmarks/biogpu_v522_biosdk_public_examples.py`, `scripts/run_biogpu_v522_biosdk_public_examples.ps1`, `docs/BIOSDK_PUBLIC_EXAMPLES_GUIDE_V522.md` and 5 focused tests.
- v5.22 moves the project from proof-only artifacts toward a user-runnable BioSDK public core without claiming full SDK or BiC OS readiness.

### 2026-05-06 — v5.23 safe user-upload fixture proof

- Added `biogpu/sdk/user_upload_fixture_v523.py`: creates a safe read-only JSON fixture under `data/external/user_upload_samples/`, validates it with v5.19 and refreshes v5.14/v5.21/v5.22 outputs.
- Added `biogpu/benchmarks/biogpu_v523_user_upload_fixture.py`, `scripts/run_biogpu_v523_user_upload_fixture.ps1`, `docs/USER_UPLOAD_FIXTURE_GUIDE_V523.md` and 5 focused tests.
- v5.23 closes the user-upload fixture path only. It does not prove vendor export portability or real external API integration.

## Claims policy

Allowed now:

- BioSDK/BioCompute Runtime prototype.
- Real-data replay evidence exists.
- Vendor-neutral architecture drafted.
- LLM/agent bridge exists for safe structured tasking, NSI manifest generation and evidence-aware responses.
- Offline control-plane queue bridge exists for approved agent/NSI manifests.
- Raw HDF5 structure and embedded event candidates have been mapped for Zenodo 14363732.
- Raw-vs-preprocessed coverage audit exists and explicitly blocks raw-equivalence overclaiming when exact recording overlap is absent.
- Raw-native HDF5 event-window feature matrix and exploratory condition readout exist over the downloaded raw archive.
- Raw-native split-half repeatability is validated, while repeated-target target-ID support is explicitly blocked by v5.9.
- v5.10 project alignment audit says the project remains on-mission and local code distinctness is supported, while global uniqueness is not locally provable.
- v5.11 BiC OS boot readiness says the offline runtime kernel can be evaluated as a composed system, while production OS readiness remains blocked by explicit subsystem gaps.
- v5.12 BioSDK evidence pack says the SDK evidence kernel can be evaluated as a capability matrix, while complete production BioSDK and global uniqueness remain unclaimed.
- v5.13 BioSDK core API says the active phase is public SDK facade work and BiC OS is locked until SDK/data/runtime gates are complete.
- v5.14 sample acquisition gate says local Zenodo proof is not enough for full SDK proof; DANDI/NWB, external read-only API/export and further public/vendor samples remain required.
- v5.15 DANDI/NWB task validation says one real DANDI sample is now locally parsed into task windows, while broader multi-source proof remains incomplete.
- v5.16 DANDI/NWB task benchmark says the DANDI sample now runs through a public SDK feature/readout/shuffle workflow, while full multi-source SDK proof remains incomplete.
- v5.17 external read-only API gate says mock adapter contracts and write denial pass locally, while real external API/export proof remains incomplete.
- v5.18 Allen orientation gate says the second independent public dataset path is now machine-tracked, while the actual Allen sample remains missing.
- v5.19 vendor/user-upload gate says private/vendor sample intake is now machine-tracked, while the actual safe sample fixtures remain missing.
- v5.20 Allen orientation benchmark says Allen public-neurophysiology parser/feature/readout evidence is now locally available from one real session.
- v5.21 says public cross-dataset BioSDK evidence can now be audited in one report, while private/external proof remains blocked.
- v5.22 says public BioSDK examples can now be run and audited, while external/vendor examples remain handoff-only.
- v5.23 says the safe user-upload path can now be validated locally, while real external API/export remains the main blocker.
- Enterprise/beta path drafted.

Not allowed yet:

- first biological computer;
- GPU replacement;
- live BioGPU proof;
- production OS;
- validated live closed loop;
- energy superiority claim.
- raw-derived feature equivalence for v15/v50 PC rows until exact raw recording overlap and waveform-derived feature rebuild are validated.
- strong raw-native performance claim from v5.8; current raw-native readout is exploratory and not statistically strong at the configured shuffle count.
- target-ID decoding claim from the current v5.9 repeated-target raw subset; target readout and fingerprint audits are not statistically supported.
- global uniqueness claim for the code or concept without external prior-art research; local tests can support local distinctness but cannot prove nobody else built similar systems.
- full BiC OS production readiness until daemon/workers, production auth, plugin manager, dashboard, live telemetry and lab approval workflow are implemented and validated.
- complete production BioSDK claim until public examples, durable scheduler, real NWB/DANDI validation, external read-only adapter validation and installable release gates are complete.

## Core target claim after PC/API validation

BioGPU-Core is the kernel of BioCompute Runtime: a vendor-neutral BioSDK and NSI interface layer for living neural compute, providing reproducible benchmarks, adapter conformance, LLM-agent integration, safety policies and auditable result bundles.


---

## v8.0 Production Release Addendum (2026-05-11)

### What changed since v5.56

After the v5.56 external-signoff-transcript-intake contract, the project
entered a deliberate production-infrastructure build phase.

### Phase 1: Production Infrastructure (v6.0-v6.12)

Closed 11 of 12 production readiness gaps from v5.49:

- v6.0: Production foundation package (`biogpu/production/`)
- v6.1-v6.5: Identity, tenants, storage, workers, registry
- v6.6: HMAC-SHA256 release signing pipeline
- v6.7: 6-gate CI/CD matrix + pre-commit hooks
- v6.8: Security threat model (5 boundaries, 5 actors, 10 controls)
- v6.9-v6.10: Incident system, notification provider
- v6.12: BiC OS production daemon + Windows service installer

One gap remains: external_beta_acceptance (requires real participants).

### Phase 2: BiC OS Unlock (v7.0)

BiC OS boot-readiness upgraded from v5.11 (offline kernel only) to v7.0
(production boot). All 6 required boot phases verified.

Result: **bic_os_phase_locked = false**. BiC OS can boot as production runtime.

### Phase 3: BiC OS Production Release (v7.1-v8.0)

- v7.1: Dashboard Control Plane (FastAPI, port 8420)
- v7.2: Plugin Manager (adapter registry, certification)
- v7.3: Live Telemetry (partner API pipeline)
- v7.4: Lab Approval Workflow (draft -> operator -> safety -> approved)
- v7.5: Safe Closed-Loop (7 safety gates, kill switch, Shannon limits)
- v8.0: Release bundle (23 subsystems, 17 production-ready)

### Honest Gaps

See `docs/HONEST_STATUS_V80.md` for detailed honest assessment.
Key gaps: replay pipeline not wired to daemon, zero live dashboard data,
no real external API validation, closed-loop never tested on hardware,
zero beta participants.

### Claims Policy Unchanged

All v5.0 claim boundaries remain in effect.


---

## v8.5 Addendum: Rebrand to BioSDK (2026-05-11)

### Why the Name Changed

The project was previously called "BiC OS" (Bio-Computer Operating System).
This was ambitious but misleading. We are NOT building an operating system
in the Linux/Windows sense. We are building a **vendor-neutral standard
interface** for biological neural data — like Vulkan for GPUs or ROS for
robotics.

### What Changed

- **Project name**: BiC OS / BioGPU-Core → **BioSDK** (BioCompute SDK)
- **Interface name**: NSI-1.0 retained (Neural Substrate Interface)
- **Runtime name**: BioCompute Runtime retained
- **Positioning**: "Operating System" → "Standard / SDK"

### What Did NOT Change

- All claim boundaries remain (no overclaiming)
- All code paths remain functional
- All evidence bundles remain verifiable
- All safety policies remain in effect
- The mission is unchanged: vendor-neutral biological neural computation

### Current State (v8.5)

See `MASTER_STATUS_V85.md` for the full current state.

Key achievements since v8.0:
- Cross-modal structure verification on 5/6 datasets
- MCS MEA2100 validated as structurally DIFFERENT from Giroldini (zero common HDF5 keys)
  → Validates the need for NSI-1.0
- 23 subsystems inventoried, 17 production-ready
- Dashboard running with real data (not zeros)

### Next Milestones

1. Cross-modal feature extraction on all 5 ready datasets
2. Sklearn baseline comparison on real feature matrices
3. First NSI-1.0 adapter certification (MCS MEA2100)
4. Consolidation to BioSDK Core v2.0

### Documents Updated

- `README.md` — complete rewrite
- `MASTER_STATUS_V85.md` — new, single source of truth
- `docs/MASTER_PROJECT_PLAN_V50.md` — this addendum
- `docs/HONEST_STATUS_V80.md` — still valid, superseded by MASTER_STATUS_V85.md
- `docs/PROJECT_DEEP_AUDIT_V85.md` — unchanged (audit is independent of name)
- `docs/UNIQUENESS_POSITIONING_V85.md` — unchanged (positioning is independent of name)


---

## v8.5 Addendum: Rebrand to BioSDK (2026-05-11)

### Why the Name Changed

The project was previously called "BiC OS" (Bio-Computer Operating System).
This was ambitious but misleading. We are NOT building an operating system
in the Linux/Windows sense. We are building a **vendor-neutral standard
interface** for biological neural data — like Vulkan for GPUs or ROS for
robotics.

### What Changed

- **Project name**: BiC OS / BioGPU-Core → **BioSDK** (BioCompute SDK)
- **Interface name**: NSI-1.0 retained (Neural Substrate Interface)
- **Runtime name**: BioCompute Runtime retained
- **Positioning**: "Operating System" → "Standard / SDK"

### What Did NOT Change

- All claim boundaries remain (no overclaiming)
- All code paths remain functional
- All evidence bundles remain verifiable
- All safety policies remain in effect
- The mission is unchanged: vendor-neutral biological neural computation

### Current State (v8.5)

See `MASTER_STATUS_V85.md` for the full current state.

Key achievements since v8.0:
- Cross-modal structure verification on 5/6 datasets
- MCS MEA2100 validated as structurally DIFFERENT from Giroldini (zero common HDF5 keys)
  → Validates the need for NSI-1.0
- 23 subsystems inventoried, 17 production-ready
- Dashboard running with real data (not zeros)

### Next Milestones

1. Cross-modal feature extraction on all 5 ready datasets
2. Sklearn baseline comparison on real feature matrices
3. First NSI-1.0 adapter certification (MCS MEA2100)
4. Consolidation to BioSDK Core v2.0

### Documents Updated

- `README.md` — complete rewrite
- `MASTER_STATUS_V85.md` — new, single source of truth
- `docs/MASTER_PROJECT_PLAN_V50.md` — this addendum
- `docs/HONEST_STATUS_V80.md` — still valid, superseded by MASTER_STATUS_V85.md
- `docs/PROJECT_DEEP_AUDIT_V85.md` — unchanged (audit is independent of name)
- `docs/UNIQUENESS_POSITIONING_V85.md` — unchanged (positioning is independent of name)


---

## v8.5 Addendum: Rebrand to BioSDK (2026-05-11)

### Why the Name Changed

The project was previously called "BiC OS" (Bio-Computer Operating System).
This was ambitious but misleading. We are NOT building an operating system
in the Linux/Windows sense. We are building a **vendor-neutral standard
interface** for biological neural data — like Vulkan for GPUs or ROS for
robotics.

### What Changed

- **Project name**: BiC OS / BioGPU-Core → **BioSDK** (BioCompute SDK)
- **Interface name**: NSI-1.0 retained (Neural Substrate Interface)
- **Runtime name**: BioCompute Runtime retained
- **Positioning**: "Operating System" → "Standard / SDK"

### What Did NOT Change

- All claim boundaries remain (no overclaiming)
- All code paths remain functional
- All evidence bundles remain verifiable
- All safety policies remain in effect
- The mission is unchanged: vendor-neutral biological neural computation

### Current State (v8.5)

See `MASTER_STATUS_V85.md` for the full current state.

Key achievements since v8.0:
- Cross-modal structure verification on 5/6 datasets
- MCS MEA2100 validated as structurally DIFFERENT from Giroldini (zero common HDF5 keys)
  → Validates the need for NSI-1.0
- 23 subsystems inventoried, 17 production-ready
- Dashboard running with real data (not zeros)

### Next Milestones

1. Cross-modal feature extraction on all 5 ready datasets
2. Sklearn baseline comparison on real feature matrices
3. First NSI-1.0 adapter certification (MCS MEA2100)
4. Consolidation to BioSDK Core v2.0

### Documents Updated

- `README.md` — complete rewrite
- `MASTER_STATUS_V85.md` — new, single source of truth
- `docs/MASTER_PROJECT_PLAN_V50.md` — this addendum
- `docs/HONEST_STATUS_V80.md` — still valid, superseded by MASTER_STATUS_V85.md
- `docs/PROJECT_DEEP_AUDIT_V85.md` — unchanged (audit is independent of name)
- `docs/UNIQUENESS_POSITIONING_V85.md` — unchanged (positioning is independent of name)
