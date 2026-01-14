from typing import List

from PySide6.QtWidgets import QVBoxLayout, QLabel

from model.data.network_verification_config import NetworkVerificationConfig
from view.base_view.insert_view import InsertView
from view.network_view.network_widget import NetworkWidget

class NetworkView(InsertView):
    pages: List[NetworkWidget]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Network"))

    def add_network(self, config: NetworkVerificationConfig):
        pass

    def open_network_file_picker(self) -> str:
        pass