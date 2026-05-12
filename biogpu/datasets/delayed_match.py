from __future__ import annotations
import numpy as np
from biogpu.datasets.orientation import _draw_line
from biogpu.schemas import InputPattern


def generate_delayed_match_dataset(
    size: int = 12,
    samples_per_class: int = 80,
    delay_frames: int = 2,
    noise: float = 0.12,
    seed: int = 123,
) -> list[InputPattern]:
    """Generate a delayed match-to-sample style dataset.

    Frame 0 is a cue orientation. After delay/noise frames, the final query frame is
    either the same orientation (label 1) or a different orientation (label 0).
    A model that sees only the last frame cannot solve it; a stateful reservoir has
    a chance because it receives the cue first and is read after the query.
    """
    rng = np.random.default_rng(seed)
    orientations = [0, 45, 90, 135]
    patterns: list[InputPattern] = []
    idx = 0
    for label in [0, 1]:
        for _ in range(samples_per_class):
            cue = int(rng.choice(orientations))
            if label == 1:
                query = cue
            else:
                query = int(rng.choice([o for o in orientations if o != cue]))
            frames = []
            cue_img = _draw_line(size, cue)
            frames.append(cue_img)
            for _d in range(delay_frames):
                # Low-structure distractor/noise frame.
                distractor = np.clip(rng.normal(0.10, noise, size=(size, size)), 0.0, 1.0).astype(np.float32)
                frames.append(distractor)
            query_img = _draw_line(size, query)
            frames.append(query_img)
            seq = np.stack(frames).astype(np.float32)
            seq = np.clip(seq + rng.normal(0.0, noise, size=seq.shape).astype(np.float32), 0.0, 1.0)
            patterns.append(InputPattern(
                id=f"delayed_match_{idx:05d}",
                data=seq,
                label=label,
                metadata={"cue": cue, "query": query, "match": bool(label), "delay_frames": delay_frames},
            ))
            idx += 1
    rng.shuffle(patterns)
    return patterns
