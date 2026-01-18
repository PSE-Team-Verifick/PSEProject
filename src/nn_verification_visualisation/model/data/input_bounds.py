from typing import Dict


class InputBounds:
    bounds: Dict[int, tuple[float, float]]

    def __init__(self, bounds: Dict[int, tuple[float, float]]):
        self.bounds = bounds