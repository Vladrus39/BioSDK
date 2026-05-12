# BioGPU v2.4 — Session Manager and Result Bundle

v2.4 adds the runtime layer that keeps BioGPU from becoming a loose collection of scripts.

## Purpose

Every run should now start from a versioned manifest and end with a reproducible result bundle.

Supported modes:

- `replay` — public real-data replay, no live hardware.
- `dry_run` — validates configuration, benchmark selection, audit logs, and bundle creation.
- `power_pc` — intended for heavy statistics, shuffles, bootstrap and large dataset runs.
- `live_lab` — future mode requiring vendor SDK, approved SOP, qualified personnel, and a live MEA/HD-MEA backend.

## Added contracts

- `BioGPURunManifest`
- `BioGPUAuditEvent`
- `BioGPUAuditLog`
- `BioGPUArtifactRef`
- `BioGPUResultBundler`
- `BioGPUSessionSummary`

## Why this matters

The future BioGPU proof needs a clean chain:

```text
benchmark selection
→ run manifest
→ mode validation
→ execution/audit log
→ results
→ result bundle
→ report/claim ladder
```

Without this layer, results from a powerful PC or live lab can easily become impossible to audit.

## Boundary

v2.4 does not add:

- wet-lab cultivation protocols;
- live stimulation limits;
- vendor pinouts;
- hardware control commands.

Those are intentionally deferred to vendor SDKs and qualified laboratory SOPs.
