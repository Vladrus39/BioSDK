# BioGPU-Core v3.8 — BioLLM Tool Interface

v3.8 turns BioGPU-Core into an LLM-callable BioSDK tool.

The intended path is:

```text
LLM / agent task
→ BioLLMTaskV38
→ BioLLMManifestV38
→ replay/mock/API read-only trace
→ BioGPUTraceV37
→ feature extraction
→ readout
→ BioLLMToolResultV38
→ structured result back to the LLM
```

## What this means commercially

This is the first enterprise-facing layer. It does not mean the customer can
immediately control a live organism. It means they can integrate BioGPU-Core into
a software/agent workflow, validate the API, read safe data streams, produce
structured outputs, and get audit/result bundles.

Commercial ladder:

1. Developer Evaluation — replay/mock/metadata validation.
2. Enterprise Read-Only BioSDK — paid connector/read-only data SDK.
3. Enterprise Live Shadow BioSDK — live read stream beside the experiment, no control.
4. Lab-Approved Closed-Loop Add-on — future premium module after vendor/lab SOP.

## Why full control is not in v3.8

Full wetware control is not a normal SDK feature; it is a regulated/lab-approved
module. v3.8 deliberately blocks live output so enterprises can safely test the
software before any live control is considered.

## Claim boundary

v3.8 proves software integration and read-only/replay tool execution. It does not
prove live BioGPU control, biological GPU replacement, or energy advantage.
