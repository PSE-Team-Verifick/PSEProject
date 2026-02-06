from __future__ import annotations

from logging import Logger
import threading
from typing import TYPE_CHECKING

from onnx import ModelProto

import numpy as np

from multiprocessing import Process, Queue

from nn_verification_visualisation.controller.process_manager.algorithm_executor import AlgorithmExecutor
from nn_verification_visualisation.model.data_loader.algorithm_file_observer import AlgorithmFileObserver
from nn_verification_visualisation.model.data.diagram_config import DiagramConfig
from nn_verification_visualisation.model.data.plot_generation_config import PlotGenerationConfig
from nn_verification_visualisation.model.data.storage import Storage
from nn_verification_visualisation.utils.result import Result, Failure, Success
from nn_verification_visualisation.view.dialogs.plot_config_dialog import PlotConfigDialog
from nn_verification_visualisation.view.plot_view.comparison_loading_widget import ComparisonLoadingWidget

if TYPE_CHECKING:
    from nn_verification_visualisation.view.plot_view.plot_view import PlotView


def execute_algorithm_wrapper(index, queue, model: ModelProto, input_bounds: np.ndarray, algorithm_path: str,
                          selected_neurons: list[tuple[int, int]]) -> None:
    try:
        executor = AlgorithmExecutor()
        execution_res = executor.execute_algorithm(model, input_bounds, algorithm_path,
                          selected_neurons)

        if not execution_res.is_success:
            queue.put((index, Failure(execution_res.error)))
            return

        output_bound_np, directions = execution_res.data

        if output_bound_np.shape[1] != 2:
            queue.put((index, Failure(Exception(f"Algorithm returned false bounds"))))
            return

        output_bounds = []
        for bounds in output_bound_np.tolist():
            output_bounds.append((bounds[0], bounds[1]))

        # Send back tuple: (index, Result)
        queue.put((index, Success((output_bounds, directions))))

    except Exception as e:
        queue.put((index, Failure(e)))


class PlotViewController:
    logger = Logger(__name__)
    current_plot_view: PlotView
    current_tab: int
    card_size: int
    plot_titles: list[str]
    diagram_selections: dict[str, set[int]]

    def __init__(self, current_plot_view: PlotView):
        self.current_plot_view = current_plot_view
        self.current_tab = 0
        self.card_size = 420
        self.plot_titles = []
        self.node_pairs = []
        self.node_pair_bounds = []
        self.node_pair_colors = []
        self.diagram_selections = {}

        #start listening for algorithm changes
        AlgorithmFileObserver()

    def change_plot(self, plot_index: int | str, add: bool, pair_index: int):
        title: str | None
        if isinstance(plot_index, int):
            if plot_index < 0 or plot_index >= len(self.plot_titles):
                return
            title = self.plot_titles[plot_index]
        else:
            title = plot_index
        if title is None:
            return
        selection = self.diagram_selections.setdefault(title, set())
        if add:
            selection.add(pair_index)
        else:
            selection.discard(pair_index)

    def start_computation(self, plot_generation_configs: list[PlotGenerationConfig]):
        logger = Logger(__name__)

        polygons: list[list[tuple[float, float]] | None] = [None] * len(plot_generation_configs)

        result_queue = Queue()
        algorithm_processes: list[Process | None] = []

        diagram_config = DiagramConfig(plot_generation_configs,polygons)

        def terminate_algorithm_process(process_index: int) -> bool:
            if process_index >= len(algorithm_processes) or not algorithm_processes[process_index]:
                return False

            process = algorithm_processes[process_index]

            if process.is_alive():
                logger.info(f"Terminating algorithm process {process_index}")
                process.terminate()
                process.join()
                result_queue.put((process_index, Failure(Exception("Cancelled by User"))))
                return True

            return False

        def result_listener():
            results_received = 0
            total_tasks = len(plot_generation_configs)

            while results_received < total_tasks:
                # wait for a result from the queue
                result_index, result = result_queue.get()

                if result.is_success:
                    bounds_list, directions_list = result.data

                    polygons[result_index] = self.compute_polygon(bounds_list, directions_list)
                else:
                    logger.error(f"Algorithm {index} failed: {result.error}")

                results_received += 1

            logger.info("All computations finished/cancelled.")
            storage = Storage()
            storage.diagrams.append(diagram_config)
            storage.request_autosave()

            print(f"Done: {results_received}/{total_tasks}, \n Polygons {str(polygons)}")

        # start algorithm processes
        for index, plot_generation_config in enumerate(plot_generation_configs):
            model: ModelProto = plot_generation_config.nnconfig.network.model
            input_bounds: np.ndarray = AlgorithmExecutor.input_bounds_to_numpy(plot_generation_config.nnconfig.bounds)
            algorithm_path: str = plot_generation_config.algorithm.path
            selected_neurons: list[tuple[int, int]] = plot_generation_config.selected_neurons

            new_process = Process(target=execute_algorithm_wrapper, args=(index, result_queue, model, input_bounds, algorithm_path, selected_neurons),)
            algorithm_processes.append(new_process)
            new_process.start()

        listener = threading.Thread(target=result_listener)
        listener.daemon = True
        listener.start()

        loading_screen = ComparisonLoadingWidget(diagram_config, terminate_algorithm_process)
        self.current_plot_view.add_loading_tab(loading_screen)

    def change_tab(self, index: int):
        pass

    def open_plot_generation_dialog(self):
        dialog = PlotConfigDialog(self)
        self.current_plot_view.open_dialog(dialog)

    def set_card_size(self, value: int):
        self.card_size = value

    def register_plot(self, title: str):
        if title in self.plot_titles:
            return
        self.plot_titles.append(title)
        self.diagram_selections.setdefault(title, set())

    def remove_plot(self, title: str):
        if title in self.plot_titles:
            self.plot_titles.remove(title)
        self.diagram_selections.pop(title, None)
    def get_node_pairs(self) -> list[str]:
        return list(self.node_pairs)

    def get_node_pair_bounds(self, index: int) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        return self.node_pair_bounds[index]

    def get_node_pair_colors(self, index: int) -> tuple[str, str]:
        return self.node_pair_colors[index]

    def get_selection(self, title: str) -> set[int]:
        return set(self.diagram_selections.get(title, set()))


    def compute_polygon(
        self, bounds: list[tuple[float, float]], directions: list[tuple[float, float]]) -> list[tuple[float, float]]:
        def clip_polygon(poly: list[tuple[float, float]], a: float, b: float, c: float):
            def inside(p: tuple[float, float]) -> bool:
                return a * p[0] + b * p[1] <= c + 1e-9

            def intersect(p1: tuple[float, float], p2: tuple[float, float]):
                x1, y1 = p1
                x2, y2 = p2
                dx = x2 - x1
                dy = y2 - y1
                denom = a * dx + b * dy
                if abs(denom) < 1e-12:
                    return p2
                t = (c - a * x1 - b * y1) / denom
                return (x1 + t * dx, y1 + t * dy)

            out: list[tuple[float, float]] = []
            for i in range(len(poly)):
                curr = poly[i]
                prev = poly[i - 1]
                curr_in = inside(curr)
                prev_in = inside(prev)
                if curr_in:
                    if not prev_in:
                        out.append(intersect(prev, curr))
                    out.append(curr)
                elif prev_in:
                    out.append(intersect(prev, curr))
            return out

        max_bound = max(abs(v) for (low, high) in bounds for v in (low, high))
        m = max(5.0, max_bound * 2.0 + 1.0)
        poly: list[tuple[float, float]] = [(-m, -m), (m, -m), (m, m), (-m, m)]

        for i, (low, high) in enumerate(bounds):
            a,b = directions[i]
            poly = clip_polygon(poly, a, b, high)
            if not poly:
                break
            poly = clip_polygon(poly, -a, -b, -low)
            if not poly:
                break
        return poly
