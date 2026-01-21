from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta

from nn_verification_visualisation.model.data.neural_network import NeuralNetwork
from nn_verification_visualisation.model.data.input_bounds import InputBounds

class InputBoundsLoader(metaclass=SingletonMeta):
    def load_input_bounds(self, file_path: str, network: NeuralNetwork) -> Result[InputBounds]:
        pass