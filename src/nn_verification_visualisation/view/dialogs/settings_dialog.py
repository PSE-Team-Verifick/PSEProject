from typing import List, Callable

from PySide6.QtWidgets import QWidget, QLabel

from nn_verification_visualisation.view.dialogs.dialog_base import DialogBase
from nn_verification_visualisation.view.dialogs.settings_option import SettingsOption

class SettingsDialog(DialogBase):
    settings: List[SettingsOption]

    def __init__(self, on_close: Callable[[], None]):
        super().__init__(on_close, "Settings")
        print("SettingsDialog init")

    def get_content(self) -> QWidget:
        return QLabel("Settings")