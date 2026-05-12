# RUN_RESULTS_REALDATA_V38

BioGPU-Core v3.8 — BioLLM Tool Interface.

## Scope

v3.8 exposes BioGPU-Core as an LLM/agent-callable BioSDK tool:

```text
LLM task → BioLLMTaskV38 → BioLLMManifestV38 → read-only/replay/API trace → BioGPUTraceV37 → features → readout → BioLLMToolResultV38
```

## Local checks performed in this environment

```text
py_compile: OK
pytest tests/test_biogpu_v38_biollm_tool_interface.py: 4 passed
v3.8 benchmark generator: OK
zip integrity: OK
```

## Demo result

```text
platforms: axion_maestro, finalspark_remote_wetware, mcs_mea2100, threebrain_hdmea
demo platform: mcs_mea2100
demo decoder: centroid_v27
demo signal: activity_detected
demo confidence: 0.5020658468796787
live_output_performed: false
```

## Output directory

```text
outputs/realdata_zenodo_14363732_v38_biollm_tool_interface/
```

Contains:

```text
BIOGPU_V38_BIOLLM_TOOL_INTERFACE_REPORT.md
v38_biollm_demo_direct.json
v38_biollm_manifest.json
v38_biollm_tool_result.json
v38_commercial_tiers.csv
v38_commercial_tiers.json
v38_summary.json
```

## Claim boundary

v3.8 is enterprise/LLM integration software only:

```text
no live actuation
no wet-lab protocol
no vendor pinout
no uncontrolled stimulation
no GPU advantage claim
```

Commercially, this is a BioSDK tiering layer: developer evaluation → enterprise read-only BioSDK → enterprise live shadow → future lab-approved closed-loop add-on.
