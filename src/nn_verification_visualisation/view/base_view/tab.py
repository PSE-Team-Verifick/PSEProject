from PySide6.QtWidgets import QWidget, QSplitter, QHBoxLayout
from PySide6.QtCore import Qt

class Tab(QWidget):
    title: str

    def __init__(self, title: str):
        super().__init__()
        self.title = title

        layout = QHBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setContentsMargins(0,0,0,0)

        splitter.addWidget(self.get_side_bar())
        splitter.addWidget(self.get_content())

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter)
        self.setLayout(layout)

    # abstract
    def get_content(self) -> QWidget:
        pass

    # abstract
    def get_side_bar(self) -> QWidget:
        pass
