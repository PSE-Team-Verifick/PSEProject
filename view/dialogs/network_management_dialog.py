from typing import Callable

from model.data.neural_network import NeuralNetwork
from view.dialogs.list_dialog_base import ListDialogBase


class NetworkManagementDialog(ListDialogBase[NeuralNetwork]):
    def __init__(self, on_close: Callable[[], None]):
        super().__init__(on_close, "Manage loaded Networks")
    pass