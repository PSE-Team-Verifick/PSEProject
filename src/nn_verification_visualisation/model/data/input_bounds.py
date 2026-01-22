from typing import Dict

import numpy as np


class InputBounds:
    bounds: Dict[int, tuple[float, float]]

    def __init__(self, bounds: Dict[int, tuple[float, float]]):
        self.bounds = bounds

    def to_numpy(self) -> np.ndarray:
        return np.asarray([self.bounds[i] for i in range(len(self.bounds))], dtype=float)
