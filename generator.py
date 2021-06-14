from abc import ABC, abstractmethod


class Generator(ABC):
    gui = None
    mesh = None
    @abstractmethod
    def generate(self):

        pass

