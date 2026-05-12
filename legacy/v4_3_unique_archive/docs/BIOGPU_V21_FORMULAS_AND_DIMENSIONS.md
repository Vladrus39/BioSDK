# BioGPU v2.1 — Formula and Dimension Book

This is the current ideal engineering sample for **BioGPU-A1**.

## Target dimensions

```text
External dry module: 90 mm x 90 mm x 25 mm
Replaceable wet cartridge: <= 60 mm x 60 mm x 15 mm
Active electrode/neural field: 4 mm x 4 mm = 16 mm^2
Bridge electrode count: 59-60 channels
Target HD-MEA electrode count: >=1024 addressable channels
Stretch HD-MEA electrode count: 4096+ channels
Nominal pitch class: 50 um
Planning pitch range: 20-200 um
Nominal recording sampling class: 20 kHz
Initial response window: 0.5 s pre + event/exact + 0.5 s post
```

## Engineering formulas

```text
A_active = W_active * H_active
N_cells = rho_cells * A_growth
pitch = W_active / (N_x - 1)
N_samples = f_s * T_window
r_i = N_spikes_i / Delta_t
Delta r_i = r_i_post - r_i_pre
Q = I * t_pulse
sigma_Q = Q / A_electrode
E_task = integral(P_total(t) dt) / N_tasks
T_loop = T_encode + T_stim + T_bio + T_acq + T_decode
AUC = P(score_positive > score_negative)
```

## Boundary

Variables such as `rho_cells`, exact surface-treatment parameters, medium composition, incubation process, and live stimulation limits are placeholders for supplier/lab SOP and vendor manuals. They are not invented in this repository.
