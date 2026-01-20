from nn_verification_visualisation.model.data.plot import Plot
from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta

class ImageExporter(metaclass=SingletonMeta):
    def export_image(self, plot: Plot, path: str) -> Result[str]:
        pass