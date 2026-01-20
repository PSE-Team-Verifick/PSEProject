from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta
from nn_verification_visualisation.model.data.algorithm import Algorithm

class AlgorithmLoader(metaclass=SingletonMeta):
    def load_algorithm(self, file_path: str) -> Result[Algorithm]:
        pass