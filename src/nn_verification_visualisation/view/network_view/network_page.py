from PySide6.QtWidgets import QWidget, QLabel

from nn_verification_visualisation.model.data.network_verification_config import NetworkVerificationConfig
from nn_verification_visualisation.view.base_view.tab import Tab
from nn_verification_visualisation.view.network_view.network_widget import NetworkWidget

class NetworkPage(Tab):
    configuration: NetworkVerificationConfig

    def __init__(self, configuration: NetworkVerificationConfig):
        self.configuration = configuration
        super().__init__(configuration.network.name)

    def get_content(self) -> QWidget:
        return NetworkWidget(self.configuration)

    def get_side_bar(self) -> QWidget:
        right = QLabel("Right (80%)")
        return right