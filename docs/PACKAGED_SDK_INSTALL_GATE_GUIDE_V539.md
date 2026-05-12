# BioGPU-Core v5.39 Packaged SDK Install Gate

v5.39 adds a packaged SDK install gate over the v5.38 storage contract.

It validates:

- `pyproject.toml` package metadata and build backend;
- package discovery for the `biogpu*` source tree;
- critical CLI entrypoint importability and callable targets;
- distribution manifest hashing;
- optional local wheel build with `pip wheel --no-deps --no-build-isolation`;
- optional local target install and import smoke from the installed wheel.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v539_packaged_sdk_install_gate.ps1
```

## Outputs

- `outputs/v539_packaged_sdk_install_gate/V539_PACKAGED_SDK_INSTALL_GATE_SUMMARY.json`
- `outputs/v539_packaged_sdk_install_gate/V539_PACKAGE_METADATA_CONTRACT.json`
- `outputs/v539_packaged_sdk_install_gate/V539_PACKAGE_DISCOVERY.json`
- `outputs/v539_packaged_sdk_install_gate/V539_ENTRYPOINT_CONTRACTS.json`
- `outputs/v539_packaged_sdk_install_gate/V539_DISTRIBUTION_MANIFEST.json`
- `outputs/v539_packaged_sdk_install_gate/V539_LOCAL_BUILD_INSTALL_RESULT.json`
- `outputs/v539_packaged_sdk_install_gate/V539_PACKAGE_INSTALL_AUDIT_BUNDLE.json`

## Missing real inputs

The local wheel build/install smoke is not a published SDK release. A full release still needs a package index or private registry, signed artifacts, provenance attestation, clean-room install validation, versioned docs, release approval and rollback policy.

## Boundary

This is a local install gate. It is not a full BioSDK release, published distribution, production BioCompute Runtime or BiC OS readiness.
