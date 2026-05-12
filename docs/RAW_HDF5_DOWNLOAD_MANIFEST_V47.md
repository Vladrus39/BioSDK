# Raw HDF5 Download Manifest — v4.7

The raw HDF5 package is intentionally not embedded. Fill the JSON template using the official dataset source before downloading.

Template path:

```text
data/templates/v47_raw_hdf5_download_manifest_template.json
```

Required fields:

- `official_download_url`
- `expected_sha256` when available
- `expected_size_bytes` when available
- `source_record_url`
- `license_or_terms`

Run:

```bash
cp data/templates/v47_raw_hdf5_download_manifest_template.json data/external/raw_hdf5_download_manifest.json
# edit the manifest
bash scripts/download_zenodo_14363732_raw_hdf5_v47.sh data/external/raw_hdf5_download_manifest.json
```

Do not run raw HDF5/TTL reconstruction until checksum and file size are verified.
