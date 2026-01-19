from typing import List
from controller.input_manager.network_view_controller import NetworkViewController

from PySide6.QtWidgets import QPushButton, QFileDialog

from model.data.network_verification_config import NetworkVerificationConfig
from model.data.storage import Storage
from view.base_view.insert_view import InsertView
from view.network_view.network_page import NetworkPage

class NetworkView(InsertView):
    # pages: List[NetworkWidget]
    controller: NetworkViewController

    def __init__(self):
        super().__init__(False)
        self.controller = NetworkViewController(self)

        self.button = QPushButton("Open Network Dialog", self)
        self.button.move(100, 80)
        self.button.clicked.connect(self.controller.open_network_management_dialog)

        self.page_layout.addWidget(self.button)

        for network in Storage().networks:
            self.add_network_tab(network)

    def add_network_tab(self, network: NetworkVerificationConfig) :
        self.tabs.add_tab(NetworkPage(network))

    def close_network_tab(self, index: int):
        self.tabs.close_tab(index)

    def open_network_file_picker(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "ONNX-Files (*.onnx);; All Files (*)")
        return file_path