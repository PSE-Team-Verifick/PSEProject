from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

from nn_verification_visualisation.view.base_view.base_view import BaseView


class MainWindow(QMainWindow):
    base_view: BaseView
    __WINDOW_TITLE: str = "PSE Neuron App"

    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.__WINDOW_TITLE)

        # Central widget (QMainWindow *requires* one)
        base_view = BaseView()

        self.setCentralWidget(base_view)