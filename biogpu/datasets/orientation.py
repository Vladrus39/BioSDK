from __future__ import annotations
import numpy as np
from biogpu.schemas import InputPattern

ORIENTATIONS = [0, 45, 90, 135]


def _draw_line(size: int, angle: int, thickness: int = 1) -> np.ndarray:
    img = np.zeros((size, size), dtype=np.float32)
    c = (size - 1) / 2.0
    if angle == 0:
        y = int(round(c))
        img[max(0, y-thickness):min(size, y+thickness+1), :] = 1.0
    elif angle == 90:
        x = int(round(c))
        img[:, max(0, x-thickness):min(size, x+thickness+1)] = 1.0
    elif angle == 45:
        for x in range(size):
            y = size - 1 - x
            for dy in range(-thickness, thickness+1):
                yy = y + dy
                if 0 <= yy < size:
                    img[yy, x] = 1.0
    elif angle == 135:
        for x in range(size):
            y = x
            for dy in range(-thickness, thickness+1):
                yy = y + dy
                if 0 <= yy < size:
                    img[yy, x] = 1.0
    else:
        raise ValueError(f"Unsupported angle: {angle}")
    return img


def generate_orientation_dataset(
    size: int = 16,
    samples_per_class: int = 80,
    noise_levels: list[float] | None = None,
    seed: int = 42,
) -> list[InputPattern]:
    rng = np.random.default_rng(seed)
    if noise_levels is None:
        noise_levels = [0.0, 0.1, 0.2, 0.3]
    patterns: list[InputPattern] = []
    idx = 0
    for label, angle in enumerate(ORIENTATIONS):
        base = _draw_line(size, angle)
        for _ in range(samples_per_class):
            noise_level = float(rng.choice(noise_levels))
            noise = rng.normal(loc=0.0, scale=noise_level, size=(size, size)).astype(np.float32)
            img = np.clip(base + noise, 0.0, 1.0)
            # Random small shift for robustness.
            shift_y = int(rng.integers(-1, 2))
            shift_x = int(rng.integers(-1, 2))
            img = np.roll(img, shift=(shift_y, shift_x), axis=(0, 1))
            patterns.append(InputPattern(
                id=f"ori_{idx:05d}",
                data=img,
                label=label,
                metadata={"angle": angle, "noise_level": noise_level, "shift": [shift_y, shift_x]},
            ))
            idx += 1
    rng.shuffle(patterns)
    return patterns
