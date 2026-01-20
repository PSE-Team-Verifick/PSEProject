from typing import List

from nn_verification_visualisation.utils.singleton import SingletonMeta
from nn_verification_visualisation.view.dialogs.info_popup import InfoPopup

class InfoPopupQueue(metaclass=SingletonMeta):
    dialogs: List[InfoPopup]

    def add(self, info_popup: InfoPopup):
        pass