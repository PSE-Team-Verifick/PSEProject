from nn_verification_visualisation.model.data.plot import Plot
from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta


class PlotExporter(metaclass=SingletonMeta):
    def export_plot(self, plot: Plot, path: str) -> Result[str]:
        pass