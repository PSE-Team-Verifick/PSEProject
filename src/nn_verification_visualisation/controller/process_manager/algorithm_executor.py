from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Callable

import numpy as np
from onnx import ModelProto

from nn_verification_visualisation.model.data.plot_generation_config import PlotGenerationConfig
from utils.result import Result, Success, Failure


class AlgorithmExecutor:
    currentAlgorithmConfig: PlotGenerationConfig

    def execute_algorithm(self, config: PlotGenerationConfig) -> Result[np.ndarray]:
        try:
            model: ModelProto = config.nnconfig.network.model
            input_bounds = config.nnconfig.bounds.to_numpy()

            fn = self._load_calculate_output_bounds(config.algorithm.path)
            output_bounds = fn(model, input_bounds)

            return Success(output_bounds)

        except BaseException as e:
            return Failure(e)

    @staticmethod
    def _load_calculate_output_bounds(file_path: str) -> Callable[[ModelProto, np.ndarray], np.ndarray]:
        path = Path(file_path)

        module_name = "nnvv_run_" + hashlib.md5(str(path.resolve()).encode("utf-8")).hexdigest()

        if module_name in sys.modules:
            del sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load algorithm module {module_name}")

        module = importlib.util.module_from_spec(spec)

        module_dir = str(path.parent.resolve())
        sys.path.insert(0, module_dir)

        try:
            spec.loader.exec_module(module)
        finally:
            if sys.path and sys.path[0] == module_dir:
                sys.path.pop(0)

        return getattr(module, "calculate_output_bounds")




