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

    def _on_menu_new(self):
        gui.Application.instance.run_in_thread(self.generate)
        #self.generate()

    def update_progress_bar(self, percent):
        self.completion_percent = percent
        gui.Application.instance.post_to_main_thread(self.AppWindow.window, self.AppWindow.update_progress_bar)
        pass


