from typing import List

from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from view.base_view.tab import Tab

class Tabs(QTabWidget):
    def __init__(self, tabs_closable: bool = False):
        super().__init__()

        self.setTabsClosable(tabs_closable)
        self.tabCloseRequested.connect(self.close_tab)

    def add_tab(self, tab: Tab):
        self.addTab(tab, tab.title)
        self.show()

    def close_tab(self, index: int):
        self.removeTab(index)
        self.show()

    def switch_tab(self, index: int):
        pass