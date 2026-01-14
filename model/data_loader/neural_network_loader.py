from utils.result import *
from utils.singleton import SingletonMeta
from model.data.neural_network import NeuralNetwork

import onnx

class NeuralNetworkLoader(metaclass=SingletonMeta):
    def load_neural_network(self, file_path: str) -> Result[NeuralNetwork]:
        try:
            model = onnx.load(file_path)
            onnx.checker.check_model(model)
            return Success(NeuralNetwork("", file_path, model))
        except BaseException as e:
            return Failure(e)