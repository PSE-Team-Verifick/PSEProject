from typing import List

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedLayout, QDialog

from view.base_view.action_menu import ActionMenu
from view.base_view.tabs import Tabs
from view.dialogs.dialog_base import DialogBase

class InsertView(QWidget):
    tabs: Tabs
    action_menu: ActionMenu
    page_layout: QVBoxLayout

    __dialog_stack: List[DialogBase]

    def __init__(self, /):
        super().__init__()

        self.tabs = Tabs()

        self.outer_layout = QStackedLayout()

        self.page_layout = QVBoxLayout()
        self.page_layout.addWidget(self.tabs)

        self.base_page = QWidget()
        self.base_page.setLayout(self.page_layout)

        self.setLayout(self.outer_layout)
        self.outer_layout.addWidget(self.base_page)

        self.__dialog_stack = []

    def open_dialog(self, dialog: DialogBase):
        self.__dialog_stack.append(dialog)
        self.outer_layout.addWidget(dialog)

    def close_dialog(self) -> bool:
        if len(self.__dialog_stack) <= 0:
            return False

        self.outer_layout.removeWidget(self.__dialog_stack.pop())
        return True
