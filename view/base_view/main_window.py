from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

from utils.singleton import SingletonMeta
from view.base_view.base_view import BaseView


class MainWindow(QMainWindow):
    base_view: BaseView
    __WINDOW_TITLE: str = "PSE Neuron App"

    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.__WINDOW_TITLE)

        # Central widget (QMainWindow *requires* one)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout for the central widget
        layout = QVBoxLayout(central_widget)

        label = QLabel("Hallo Cedric!", self)
        layout.addWidget(label)