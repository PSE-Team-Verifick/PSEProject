from typing import List

from nn_verification_visualisation.view.dialogs.dialog_base import DialogBase
from nn_verification_visualisation.view.dialogs.settings_option import SettingsOption

class SettingsDialog(DialogBase):
    settings: List[SettingsOption]