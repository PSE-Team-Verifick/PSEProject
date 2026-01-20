from nn_verification_visualisation.utils.result import Result
from nn_verification_visualisation.utils.singleton import SingletonMeta
from nn_verification_visualisation.model.data.save_state import SaveState

class SaveStateExporter(metaclass=SingletonMeta):
    def export_save_state(self, save_state: SaveState) -> Result[str]:
        pass