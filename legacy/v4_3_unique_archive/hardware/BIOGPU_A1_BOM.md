# BioGPU-A1 Bill of Materials / Component Classes

This BOM is a **component-class BOM**, not a purchase order. Exact models depend on chosen vendor, lab SOP and budget.

## wet_cartridge — Replaceable living neural cartridge

- Layer: `wetware`
- Stage: `licensed_lab`
- Criticality: `required`
- Role: Physical living substrate chamber containing neuronal culture over MEA/HD-MEA.
- Target spec: Transparent sealed/controlled cartridge; first target 2D neuronal network over electrode array; final geometry depends on selected MEA vendor.
- Bridge options: 60/120/256 electrode MEA cartridge/dish class, single-well MEA cartridge
- Target options: 4096+ channel HD-MEA single-well cartridge, future 3D organoid/neurosphere cartridge

## mea_chip — MEA/HD-MEA electrode chip

- Layer: `bioelectronic_interface`
- Stage: `licensed_lab`
- Criticality: `required`
- Role: Bidirectional interface: stimulate selected sites and record extracellular activity.
- Target spec: Bridge: 59-256 electrode MEA. Target: 1024-4096+ addressable HD-MEA channels. Planning pitch class 20-200 µm.
- Bridge options: MCS MEA2100-compatible 60/120/256 electrode MEA, Axion Maestro-compatible MEA plate
- Target options: 3Brain CorePlate/BioCAM-class 4096 electrode HD-MEA, future higher-density HD-MEA

## headstage_stimulator — Headstage, amplifier and stimulator

- Layer: `electronics`
- Stage: `licensed_lab`
- Criticality: `required`
- Role: Low-noise acquisition, ADC, stimulation command execution, timestamping.
- Target spec: Bidirectional acquisition/stimulation system with API/SDK access, timestamping, and export of raw traces/spikes.
- Bridge options: MCS MEA2100 headstage/stimulator, Axion Maestro-class acquisition/stimulation backend
- Target options: 3Brain BioCAM/BioCAM DupleX-class HD-MEA backend, Intan RHS-class research controller where appropriate

## environment_control — Environmental control module

- Layer: `life_support`
- Stage: `licensed_lab`
- Criticality: `required`
- Role: Maintain stable conditions around the living substrate.
- Target spec: Temperature, CO2, humidity, vibration/noise isolation, and sensor telemetry suited to selected wetware platform.
- Bridge options: built-in MEA stage-top temperature control, integrated incubated multiwell MEA chamber
- Target options: closed cartridge environment with telemetry export, long-run incubated HD-MEA setup

## microfluidics — Microfluidics / media maintenance module

- Layer: `life_support`
- Stage: `future`
- Criticality: `recommended`
- Role: Support long-running wetware operation through medium handling and monitoring.
- Target spec: Perfusion/media exchange capability or vendor-supported maintenance mode, with logging and alarms.
- Bridge options: manual/vender-SOP maintenance for short bridge runs
- Target options: closed-loop microfluidic cartridge, remote-access wetware platform model

## host_pc — BioGPU controller workstation

- Layer: `compute`
- Stage: `now`
- Criticality: `required`
- Role: Runs BioGPU runtime, adapters, feature extraction, readout, benchmark orchestration and logging.
- Target spec: Minimum: 8 cores, 32 GB RAM, 1 TB SSD for full local runs. Better: 16+ cores, 64 GB RAM, 2+ TB SSD.
- Bridge options: Ubuntu workstation, lab PC attached to vendor acquisition system
- Target options: dedicated acquisition PC + analysis workstation pair, server with NAS for long recordings

## storage — Data storage and result bundle store

- Layer: `compute`
- Stage: `now`
- Criticality: `required`
- Role: Stores raw traces, spikes, BioGPUTrace, BioGPUResult, logs, reports and audit manifests.
- Target spec: SSD/NVMe for active runs; external or NAS backup for raw traces and long experiments.
- Bridge options: local SSD for replay datasets, USB/NAS backup
- Target options: RAID/NAS storage with immutable run bundles

## runtime — BioGPU runtime software

- Layer: `software`
- Stage: `now`
- Criticality: `required`
- Role: Defines BioGPUJob → substrate adapter → BioGPUTrace → readout → BioGPUResult.
- Target spec: Same job contract must run in replay, dry-run and live modes.
- Bridge options: RealDataReplayBioGPUSubstrate, dry-run vendor adapter
- Target options: LiveMEA adapter with vendor backends

## visual_monitoring — Optional microscope / camera monitoring

- Layer: `monitoring`
- Stage: `future`
- Criticality: `optional`
- Role: Provides visual QC of cartridge condition and experiment state.
- Target spec: Optional microscope/camera stream linked to run logs.
- Bridge options: manual microscope QC
- Target options: integrated imaging with timestamps

## power_ups — Power, UPS and telemetry

- Layer: `infrastructure`
- Stage: `power_pc`
- Criticality: `recommended`
- Role: Stabilizes long-running experiments and tracks power for energy-per-task calculations.
- Target spec: UPS, watt meter, per-device power logging where possible.
- Bridge options: external watt meter for host + electronics
- Target options: per-module telemetry feed into BioGPU metrics

## sop_safety — Lab SOP, ethics and biosafety boundary

- Layer: `governance`
- Stage: `licensed_lab`
- Criticality: `required`
- Role: Defines what can be done live, by whom, and with which vendor/lab-approved procedures.
- Target spec: Approved SOPs, vendor manuals, trained personnel, facility approval as applicable.
- Bridge options: no live culture work in software-only environment
- Target options: qualified lab deployment package
