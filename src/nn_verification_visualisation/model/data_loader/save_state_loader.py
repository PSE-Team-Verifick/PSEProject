from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta
from nn_verification_visualisation.model.data.save_state import SaveState

class SaveStateLoader(metaclass=SingletonMeta):
    def load_save_state(self, file_path: str) -> Result[SaveState]:
        pass