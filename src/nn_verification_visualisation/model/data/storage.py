from typing import List

from nn_verification_visualisation.model.data.diagram_config import DiagramConfig
from nn_verification_visualisation.model.data.network_verification_config import NetworkVerificationConfig
from nn_verification_visualisation.utils.singleton import SingletonMeta


class Storage(metaclass=SingletonMeta):
    networks: List[NetworkVerificationConfig]
    diagrams: List[DiagramConfig]

    def __init__(self):
        self.networks = []
        self.diagrams = []