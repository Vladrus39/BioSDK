# RUN RESULTS — BioGPU-Core v1.5 pulse-level readout

Dataset: uploaded `Pre_processed_MEA_data.zip`.

Output directory:

```text
outputs/realdata_zenodo_14363732_v15_readout/
```

## Feature vectors

```text
pulse windows: 11,547
recordings with protocols: 41
cultures: 18
electrodes: 59
features per pulse: 354
feature matrix shape: (11547, 354)
conditions:
  lightstim: 11,367
  elecstim: 180
```

## Target-ID readout — all conditions

Leave-one-culture-out, standardized nearest-centroid readout.

```text
samples: 11,547
target classes: 27
accuracy: 0.10245
balanced accuracy: 0.07296
test label seen fraction: 0.63081
seen-label accuracy: 0.16241
top-3 accuracy: 0.15103
seen-label top-3 accuracy: 0.23943
```

Label-shuffled baseline was run with 1 shuffle for this strict multiclass readout due runtime limits:

```text
shuffle accuracy: 0.05733
shuffle seen-label accuracy: 0.09088
```

Interpretation: target-ID classification is weak, but above the single shuffled run. This result must not be overclaimed because many targets are culture-confounded or unseen in held-out folds.

## Target-ID readout — LightStim only

```text
samples: 11,367
target classes: 25
accuracy: 0.10654
balanced accuracy: 0.08039
test label seen fraction: 0.60913
seen-label accuracy: 0.17490
top-3 accuracy: 0.14956
seen-label top-3 accuracy: 0.24552
```

Single label-shuffled baseline:

```text
shuffle accuracy: 0.00317
shuffle seen-label accuracy: 0.00520
```

Interpretation: LightStim-only target-ID readout also remains limited by target/culture coverage.

## Candidate target-vs-random electrode readout

This is the main v1.5 separability result.

Task:

```text
true target electrode response vs one same-pulse random non-target electrode
```

Leave-one-culture-out, 50 label shuffles.

```text
candidate samples: 23,094
pulse windows used: 11,547
positive fraction: 0.5
accuracy: 0.78943
balanced accuracy: 0.78943
ROC AUC: 0.90059
```

Shuffled baseline:

```text
ROC AUC median: 0.50414
ROC AUC 5%-95%: 0.38634 - 0.59758
balanced accuracy median: 0.50219
balanced accuracy 5%-95%: 0.41467 - 0.58176
p-value ROC AUC > shuffle: 0.01961
p-value balanced accuracy > shuffle: 0.01961
```

## Honest conclusion

v1.5 confirms real pulse-level separability:

```text
real spike-response features
+ leave-one-culture-out train/test
+ target-vs-random readout
+ 50x label-shuffled baseline
=> observed ROC AUC 0.90059 vs shuffled median 0.50414
```

This is a strong biological-response separability result. It is still not a full BioGPU advantage claim.
