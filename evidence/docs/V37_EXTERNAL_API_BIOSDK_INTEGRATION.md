# BioGPU-Core v3.7 — External API / BioSDK Integration Skeleton

v3.7 prepares BioGPU-Core to become a commercial BioSDK. It adds a standard external API contract for FinalSpark-class, 3Brain-class, Axion-class and MCS/MEA2100-class integrations.

## Intended commercial meaning

This is not a permanently restricted toy version. It is the safe onboarding layer:

1. **Evaluation / mock / metadata-only** — enterprises can validate installation, schemas and result bundles.
2. **Enterprise read-only SDK** — paid integration to read or import data from real systems.
3. **Live shadow mode** — read live streams and produce predictions, without controlling the wetware.
4. **Lab-approved closed-loop module** — future high-value module, enabled only under vendor/lab-approved protocols.

## Why not full live control immediately?

Because full control without staged validation is a liability. v3.7 makes the SDK easier to adopt commercially: labs can trust it first as a read-only observer, then gradually authorize higher-risk modules.

## Explicitly blocked in v3.7

- live stimulation
- electrode control
- physical wiring/pinout
- environment/media control
- wet-lab recipes
- unchecked closed-loop actuation

## Enabled in v3.7

- metadata
- mock client validation
- read-only spike event export
- read-only trace export
- BioGPUTrace conversion
- commercial tier definitions
- result bundle generation
