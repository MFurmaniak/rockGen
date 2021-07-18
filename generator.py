from abc import ABC, abstractmethod
import open3d.visualization.gui as gui


class Generator(ABC):
    gui = None
    mesh = None
    completion_percent = 0
    operations_number = 0
    max_operations_number = 0

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def set_operation_number(self):
        pass

    def reset_operations_counter(self):
        self.operations_number = 0
        self.set_operation_number()
        self.update_progress_bar(0)

    def increment_and_display_operations(self):
        self.operations_number += 1
        self.update_progress_bar(self.operations_number / self.max_operations_number)

    def __init__(self, app_window):
        self.AppWindow = app_window
        self._new_button = gui.Button("Generate")
        self._new_button.set_on_clicked(self._on_generate_button)

    def _on_generate_button(self):

        gui.Application.instance.run_in_thread(self.prepare_and_generate)
        #self.generate()

    def prepare_and_generate(self):
        self._new_button.enabled = False
        self.reset_operations_counter()
        self.generate()
        self._new_button.enabled = True
        gui.Application.instance.post_to_main_thread(self.AppWindow.window, self.AppWindow.display_mesh)

    def update_progress_bar(self, percent):
        self.completion_percent = percent
        gui.Application.instance.post_to_main_thread(self.AppWindow.window, self.AppWindow.update_progress_bar)
        pass


