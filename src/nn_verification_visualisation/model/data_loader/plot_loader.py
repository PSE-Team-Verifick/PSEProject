from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta
from nn_verification_visualisation.model.data.plot import Plot

class PlotLoader(metaclass=SingletonMeta):
    def load_plot(self, file_path: str) -> Result[Plot]:
        pass