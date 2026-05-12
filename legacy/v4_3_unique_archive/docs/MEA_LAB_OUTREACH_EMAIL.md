# MEA laboratory outreach email draft

## Subject

Collaboration proposal: software scaffold for MEA-based biological reservoir computing

## Email

Good day,

My name is Vladislav Dobrovolskii. I am developing an open research project called BioGPU-Core, focused on testing whether living neuronal cultures on MEA/HD-MEA platforms can be used as biological reservoir computing substrates for simple pattern, temporal-memory and streaming benchmarks.

The project is not a wet-lab protocol and does not attempt to provide biological procedures. It is a software and measurement scaffold designed to support:

- event/stimulation encoding;
- MEA adapter abstraction;
- spike/activity feature extraction;
- baseline-controlled decoding;
- repeated-seed evaluation;
- energy accounting hooks;
- HDF5/NWB-like data export;
- reproducible reports and dashboards.

The current software already runs with a simulated MEA and includes benchmark tasks such as delayed match, streaming change detection, orientation detection and reservoir ablations. The honest current conclusion is that simulation alone is not enough; we need real neural activity data or collaboration with an MEA-equipped laboratory.

I would like to ask whether your laboratory would be open to discussing a small collaboration where we provide the software/analysis stack and adapt it to your MEA data format, while your team provides either:

1. an existing anonymized MEA dataset from neuronal cultures, or
2. guidance on adapting the pipeline to your MEA recording/stimulation workflow, or
3. a small pilot experiment using your established protocols and equipment.

We are especially interested in pattern-response separability, temporal memory, robustness to noise and honest comparison against shuffled/random/digital baselines.

The project does not require any change to your biological protocols at the first stage. The first useful step could be offline analysis of existing MEA recordings.

Kind regards,
Vladislav Dobrovolskii
