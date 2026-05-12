# BioGPU-Core v4.5 Repository Cleanup Audit

## Direct answer

Yes: before v4.5, the complete plan was spread across many docs and version outputs. This is normal for rapid research iteration, but it is not acceptable for beta/enterprise delivery. v4.5 fixes this by adding one master plan, one document index, one cleanup audit, and one beta/enterprise entry point.

## Cleanup items

### documentation
- Problem: Roadmap and strategy are spread across many versioned docs
- Action: Use docs/MASTER_PROJECT_PLAN_V45.md as single source of truth; treat older docs as historical evidence
- Risk if ignored: testers and partners cannot understand current direction

### repository
- Problem: Many PROJECT_INVENTORY_V*.md and RUN_RESULTS_REALDATA_V*.md files clutter root
- Action: Before beta, move historical inventories/results into archive/history or generated_reports
- Risk if ignored: root looks unprofessional and confusing

### outputs
- Problem: Multiple outputs/realdata_* folders accumulate generated artifacts
- Action: Keep latest beta outputs; archive old generated outputs outside source tree
- Risk if ignored: zip grows and hides important files

### docs
- Problem: Wetware/blueprint docs mix current safe SDK with speculative/live lab notes
- Action: Add docs/DOCUMENT_INDEX_V45.md and mark documents as current/reference/legacy/restricted
- Risk if ignored: safety and commercial story becomes unclear

### packaging
- Problem: Some previous generated zips were missing from local file list or based on older archive
- Action: Use release manifest and zip integrity check for every release
- Risk if ignored: users may receive inconsistent packages

### tests
- Problem: Targeted tests exist, but no single beta acceptance test suite
- Action: Add beta acceptance checklist and smoke workflow
- Risk if ignored: external testers may test different things

### data
- Problem: Only a small preprocessed real dataset has been run locally
- Action: Power-PC validation must add raw HDF5, DANDI/NWB, AllenSDK, and user uploads
- Risk if ignored: claims remain too narrow

## Policy
Do not delete historical artifacts immediately. For beta packaging, hide/archive them from the user-facing root and expose only current docs, sample manifests, scripts, and selected result bundles.
