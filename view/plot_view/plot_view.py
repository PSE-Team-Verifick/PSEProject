from PySide6.QtWidgets import QVBoxLayout, QLabel

from view.base_view.insert_view import InsertView


class PlotView(InsertView):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Plot"))