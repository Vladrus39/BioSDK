# RealMEAAdapter contract

`RealMEAVendorNeutralAdapter` is a safe dry-run skeleton for future MEA/HD-MEA integration.

It exists so BioGPU can be developed against a stable software interface before laboratory hardware access exists.

## Current status

- Dry-run only.
- No hardware connection.
- No biological stimulation parameters.
- Empty spike train returned intentionally.
- Full implementation must be provided by a lab-approved vendor SDK adapter.

## Contract methods

```python
connect()
configure(config)
send_stimulation(pattern)
read_spikes(window_ms)
read_raw(window_ms)
health_check()
close()
```

## Future vendor adapters

Possible future implementations:

```text
MaxWell/MaxOne-like adapter
Multi Channel Systems adapter
OpenMEA adapter
FinalSpark remote adapter
CL1 remote adapter
```

## Project rule

Core BioGPU modules must depend on `ComputeSubstrateAdapter`, not on a specific vendor.
