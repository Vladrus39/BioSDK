from __future__ import annotations
from biogpu.datasets.orientation import generate_orientation_dataset


def generate_noise_robustness_dataset(size: int = 16, samples_per_class: int = 40, noise_levels=None, seed: int = 43):
    if noise_levels is None:
        noise_levels = [0.0, 0.15, 0.3, 0.45, 0.6]
    return generate_orientation_dataset(size=size, samples_per_class=samples_per_class, noise_levels=list(noise_levels), seed=seed)
