# RUN RESULTS — BioGPU v2.1 Ideal Working Sample

## Scope

v2.1 adds the ideal engineering sample for the first real BioGPU-A1 path:

- physical dimensions and geometry variables;
- wetware component stack;
- high-level connection map;
- formula book;
- session schema;
- result bundle exporter;
- benchmark registry.

## Boundary

This is not a wet-lab operating protocol. Exact concentrations, cell handling, incubation timing, seeding density and live stimulation limits must be provided by qualified SOPs and vendor manuals.

## Expected checks

```text
pytest -q tests/test_biogpu_v21_wetware.py tests/test_biogpu_v21_wetware_session.py tests/test_biogpu_v21_registry.py
```
