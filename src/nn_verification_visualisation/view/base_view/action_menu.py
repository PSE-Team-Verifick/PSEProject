from typing import List

from PySide6.QtWidgets import QWidget

from nn_verification_visualisation.view.base_view.action_menu_item import ActionMenuItem

class ActionMenu(QWidget):
    items: List[ActionMenuItem]