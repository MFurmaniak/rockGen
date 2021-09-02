from abc import ABC, abstractmethod
import open3d.visualization.gui as gui
import open3d as o3d
import numpy as np


class Generator(ABC):
    gui = None
    mesh = None
    _mesh_choice = None
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


    def create_mesh_choice(self, index = 0):
        self._mesh_choice = gui.Combobox()
        self._mesh_choice.add_item("Tetrahedron")
        self._mesh_choice.add_item("Octahedron")
        self._mesh_choice.add_item("Icosahedron")
        self._mesh_choice.add_item("Cube")
        self._mesh_choice.add_item("Box")
        self._mesh_choice.add_item("Sphere")
        self._mesh_choice.selected_index = index

    def create_base_mesh(self):
        index = self._mesh_choice.selected_index
        if index == 0:
            self.mesh = o3d.geometry.TriangleMesh.create_tetrahedron()
        elif index == 1:
            self.mesh = o3d.geometry.TriangleMesh.create_octahedron()
        elif index == 2:
            self.mesh = o3d.geometry.TriangleMesh.create_icosahedron()
        elif index == 3:
            self.mesh = o3d.geometry.TriangleMesh.create_box()
            self.center_mesh(self.mesh)
        elif index == 4:
            self.mesh = o3d.geometry.TriangleMesh.create_box(width=2)
            self.center_mesh(self.mesh)
        elif index == 5:
            self.mesh = o3d.geometry.TriangleMesh.create_sphere(resolution=6)

    def center_mesh(self, mesh):
        vertices = np.asarray(mesh.vertices)
        # mesh.translate(-(np.amin(vertices, axis=0) + np.amax(vertices, axis=0)) / 2)
        mesh.translate(-vertices.mean(axis=0))

