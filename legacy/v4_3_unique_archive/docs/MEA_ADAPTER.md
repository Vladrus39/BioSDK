# MEA Adapter

The adapter isolates BioGPU core logic from hardware details.

```python
connect()
configure(config)
send_stimulation(pattern)
read_spikes(window_ms)
read_raw(window_ms)
health_check()
close()
```

v0.1 includes `SimulatedMEA` only. Future adapters should implement device APIs while respecting lab safety and manufacturer documentation.
