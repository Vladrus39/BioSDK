from __future__ import annotations

import numpy as np
from biogpu.schemas import InputPattern
from biogpu.datasets.orientation import _draw_line


def generate_streaming_change_dataset(
    size: int = 12,
    samples_per_class: int = 80,
    sequence_length: int = 6,
    noise: float = 0.10,
    seed: int = 515,
) -> list[InputPattern]:
    """Generate streaming sequences where the label depends on an online change.

    Classes:
      0: stable orientation across the stream
      1: orientation changes halfway through the stream

    This is intentionally closer to an online wetware task than a static image
    task: a reservoir can use state/history, while a last-frame-only baseline
    loses part of the evidence.
    """
    rng = np.random.default_rng(seed)
    orientations = [0, 45, 90, 135]
    patterns: list[InputPattern] = []
    for label in [0, 1]:
        for i in range(samples_per_class):
            start = int(rng.choice(orientations))
            if label == 0:
                second = start
            else:
                choices = [o for o in orientations if o != start]
                second = int(rng.choice(choices))
            frames = []
            for t in range(sequence_length):
                orient = start if t < sequence_length // 2 else second
                frame = _draw_line(size, orient)
                # Add changing distractor noise to make raw memorization less trivial.
                frame = np.clip(frame + rng.normal(0.0, noise, size=(size, size)), 0.0, 1.0)
                if rng.random() < 0.35:
                    # transient distractor dot
                    rr, cc = rng.integers(0, size, size=2)
                    frame[rr, cc] = 1.0
                frames.append(frame.astype(np.float32))
            patterns.append(InputPattern(
                id=f"stream_{label}_{i}",
                data=np.asarray(frames, dtype=np.float32),
                label=label,
                metadata={"task": "streaming_change", "start_orientation": start, "second_orientation": second},
            ))
    rng.shuffle(patterns)
    return patterns
