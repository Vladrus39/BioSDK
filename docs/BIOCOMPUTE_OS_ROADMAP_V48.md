# BioCompute OS Roadmap v4.8

The project should evolve by layers, not by prematurely claiming to be an operating system.

## Stage R0 — Evidence-preserving research archive

Status: present in v4.7/v4.8 evidence pack.

Purpose: preserve all real-data evidence, matrices and reports: v12, v15, v32, v33, v36 and later.

## Stage R1 — BioSDK / Living Compute SDK

Purpose: developer-facing SDK for replay, dataset import, read-only API integration, adapter writing, readouts and result bundles.

Required before beta:

- stable CLI commands;
- schemas for task manifests and bundles;
- sample manifests;
- dataset asset registry;
- adapter conformance tests.

## Stage R2 — BioCompute Runtime

Purpose: runtime that executes manifests, validates safety policy, runs benchmarks/readouts and creates result bundles.

Required:

- stable manifest runner;
- job runner;
- benchmark registry;
- audit logging;
- bundle generator.

## Stage R3 — NSI-1.0 / Neural Substrate Interface

Purpose: vendor-neutral interface profile over NWB/HDF5/vendor exports/API streams.

Core schemas:

- BioComputeTrace;
- BioComputeTaskManifest;
- BioComputeFeatureBatch;
- BioComputeReadoutResult;
- BioComputeResultBundle;
- BioComputeSafetyProfile;
- BioComputeAdapterContract.

## Stage R4 — BioCompute Control Plane

Purpose: hosted/on-prem server layer for users, jobs, datasets, storage, quotas, API keys, audit and dashboards.

Required before enterprise SaaS:

- auth;
- database;
- persistent job queue;
- object storage;
- team workspaces;
- admin dashboard;
- rate limits;
- billing hooks.

## Stage R5 — BioCompute OS

Purpose: long-term OS-like layer for living compute.

Do not claim OS status until these exist:

- persistent daemon/service;
- device/session manager;
- scheduler;
- permission system;
- plugin/adapter system;
- live telemetry;
- safety supervisor;
- lab-approved operator workflow;
- real device/API adapters;
- conformance tests.
