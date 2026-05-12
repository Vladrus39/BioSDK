# BioGPU Formula Book v2.1

The project uses formulas for **design, measurement and benchmarking**, not as a standalone wet-lab recipe.

Core formulas:

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

Live stimulation formulas are stored only as audit placeholders. Actual safe limits must come from vendor documentation and approved laboratory SOP.
