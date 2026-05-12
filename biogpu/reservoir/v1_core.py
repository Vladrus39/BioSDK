from __future__ import annotations
from dataclasses import dataclass
import numpy as np
try:
    from scipy.signal import correlate2d
except Exception:  # pragma: no cover
    correlate2d = None

@dataclass
class V1CoreConfig:
    """Lightweight V1-inspired feature extractor.

    This is an engineering abstraction, not a biologically exact V1 model.
    It implements: local receptive fields, orientation-like filter banks,
    rectification, optional lateral inhibition and sparse feature maps.
    """
    image_size: int = 16
    inhibition_strength: float = 0.35
    sparse_threshold: float = 0.02

class V1Core:
    ORIENTATIONS = (0, 45, 90, 135)

    def __init__(self, config: V1CoreConfig | None = None):
        self.config = config or V1CoreConfig()
        self.kernels = self._build_kernels()

    @staticmethod
    def _build_kernels() -> dict[int, np.ndarray]:
        # Simple edge/orientation filters. They are intentionally tiny and transparent.
        return {
            0: np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32),
            90: np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32),
            45: np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]], dtype=np.float32),
            135: np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]], dtype=np.float32),
        }

    @staticmethod
    def _conv2d_same(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        image = np.asarray(image, dtype=np.float32)
        if correlate2d is not None:
            return correlate2d(image, kernel, mode='same', boundary='symm').astype(np.float32)
        padded = np.pad(image, 1, mode='edge')
        out = np.zeros_like(image, dtype=np.float32)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                out[y, x] = float(np.sum(padded[y:y+3, x:x+3] * kernel))
        return out

    def transform_maps(self, image: np.ndarray) -> dict[int, np.ndarray]:
        """Return sparse orientation response maps."""
        responses = {ori: np.maximum(0.0, self._conv2d_same(image, k)) for ori, k in self.kernels.items()}
        # Local competition across orientations at every spatial position.
        stack = np.stack([responses[o] for o in self.ORIENTATIONS], axis=0)
        winner = np.max(stack, axis=0, keepdims=True)
        inhibited = np.maximum(0.0, stack - self.config.inhibition_strength * (winner - stack))
        inhibited[inhibited < self.config.sparse_threshold] = 0.0
        return {ori: inhibited[i] for i, ori in enumerate(self.ORIENTATIONS)}

    def transform_vector(self, image: np.ndarray) -> np.ndarray:
        maps = self.transform_maps(image)
        return np.concatenate([maps[o].reshape(-1) for o in self.ORIENTATIONS]).astype(np.float32)

    def dominant_orientation(self, image: np.ndarray) -> int:
        maps = self.transform_maps(image)
        scores = {ori: float(np.sum(val)) for ori, val in maps.items()}
        return max(scores, key=scores.get)
