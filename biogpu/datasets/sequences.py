from __future__ import annotations
import numpy as np
from biogpu.schemas import InputPattern

SYMBOLS = [0, 1, 2]
SEQUENCE_CLASSES = {
    (0, 1, 2): 0,
    (2, 1, 0): 1,
    (0, 2, 1): 2,
    (1, 2, 0): 3,
}


def _symbol_pattern(symbol: int, size: int, rng: np.random.Generator, noise: float) -> np.ndarray:
    img = np.zeros((size, size), dtype=np.float32)
    if symbol == 0:
        img[size//2, :] = 1.0
    elif symbol == 1:
        img[:, size//2] = 1.0
    elif symbol == 2:
        np.fill_diagonal(img, 1.0)
    else:
        raise ValueError(symbol)
    if noise > 0:
        img = np.clip(img + rng.normal(0, noise, size=img.shape).astype(np.float32), 0, 1)
    return img


def generate_sequence_dataset(size: int = 12, samples_per_class: int = 50, noise: float = 0.15, seed: int = 99) -> list[InputPattern]:
    """Generate sequence patterns where order matters.

    Each sample is stored as a 3 x H x W tensor. Classes contain the same symbol
    components in different orders, so a reservoir with state/memory is useful.
    """
    rng = np.random.default_rng(seed)
    patterns: list[InputPattern] = []
    idx = 0
    for seq, label in SEQUENCE_CLASSES.items():
        for _ in range(samples_per_class):
            frames = [_symbol_pattern(s, size, rng, noise=noise) for s in seq]
            data = np.stack(frames, axis=0).astype(np.float32)
            patterns.append(InputPattern(id=f"seq_{idx:05d}", data=data, label=label, metadata={"sequence": list(seq), "noise": noise}))
            idx += 1
    rng.shuffle(patterns)
    return patterns
