from abc import ABC, abstractmethod
import open3d.visualization.gui as gui


class Generator(ABC):
    gui = None
    mesh = None
    @abstractmethod
    def generate(self):

        pass

    def _on_menu_new(self):
        gui.Application.instance.run_in_thread(self.generate)
        #self.generate()

