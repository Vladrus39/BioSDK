# BioGPU High-Level Connection Architecture

## System-level chain

1. task input enters the BioGPU runtime;
2. encoder converts the task into a substrate-facing request;
3. stimulus planner prepares a safe high-level command;
4. vendor hardware backend sends the command to stimulation/acquisition electronics;
5. electronics interface with the MEA/HD-MEA chip;
6. the chip interfaces with the living neuronal network;
7. biological response returns through the same chip/electronics path;
8. BioGPU runtime stores traces, extracts features and runs readout;
9. benchmark harness scores the result and optionally schedules the next closed-loop step.

## Not included here

This document is architectural only. It deliberately does **not** specify:

- live pinouts;
- vendor wiring diagrams;
- electrical safety limits;
- live stimulation settings.

Those belong to the real vendor backend and qualified lab SOPs.
