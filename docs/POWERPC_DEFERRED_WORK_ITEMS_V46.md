# BioGPU v4.6 Deferred Work Items for Powerful PC

| ID | Item | Required before beta | Notes |
|---|---|---:|---|
| PC0 | Repeat smoke tests on target PC | yes | Validate environment first |
| PC1 | Validate full Pre_processed_MEA_data.zip | yes | SHA256 must match manifest |
| PC2 | Repeat compact lineage-strict sweep | yes | Confirms no environment drift |
| PC3 | full_shuffle_1000 | yes | Main statistical validation |
| PC4 | extended_methods_5000 | no | Supplementary heavy run |
| PC5 | Raw HDF5/TTL download and inspection | yes | Needed for pulse-level truth |
| PC6 | Raw-derived windows vs preprocessed features | yes | Critical scientific bridge |
| PC7 | DANDI/NWB discovery parser | no | Dataset expansion |
| PC8 | AllenSDK orientation benchmark | no | Independent task benchmark |
| PC9 | Latency/energy measurement | yes | Needed for performance claims |
| PC10 | Final PC result bundle | yes | Release gate artifact |
