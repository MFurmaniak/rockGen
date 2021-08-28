from generator import Generator
import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui


class SphereInflationGenerator(Generator):
    dfactor = 0.8
    iterations = 2
    min_displacement = 15
    max_displacement = 30
    seed = 0
    rng = None
    smoothing = True

    def __init__(self, app_window):
        super().__init__(app_window)
        self.create_mesh_choice()
        em = app_window.window.theme.font_size
        rock_settings = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        rock_settings.add_child(gui.Label("Sphere Inflation Generator"))
        grid = gui.VGrid(2, 0.25 * em)
        rock_settings.add_child(grid)
        grid.add_child(gui.Label("Base shape"))
        grid.add_child(self._mesh_choice)
        grid.add_child(gui.Label("Seed"))
        self._seed_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._seed_input.set_on_value_changed(self._on_seed_change)
        grid.add_child(self._seed_input)

        grid.add_child(gui.Label("Subdivision iterations"))
        self._sub_iterations_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._sub_iterations_input.set_on_value_changed(self._on_iter_change)
        self._sub_iterations_input.set_value(self.iterations)
        grid.add_child(self._sub_iterations_input)

        grid.add_child(gui.Label("Dampening factor"))
        self._dampening_factor = gui.Slider(gui.Slider.DOUBLE)
        self._dampening_factor.set_limits(0, 1)
        self._dampening_factor.set_on_value_changed(self._on_dfactor_change)
        self._dampening_factor.double_value = self.dfactor
        grid.add_child(self._dampening_factor)

        rock_settings.add_child(gui.Label("Deformation values"))
        grid = gui.VGrid(2, 0.25 * em)

        grid.add_child(gui.Label("Minimal displacement"))
        self._min_def_val = gui.Slider(gui.Slider.INT)
        self._min_def_val.set_limits(-30, 100)
        self._min_def_val.set_on_value_changed(self._on_min_def_value_change)
        self._min_def_val.double_value = self.min_displacement
        grid.add_child(self._min_def_val)

        grid.add_child(gui.Label("Maximum displacement"))
        self._max_def_val = gui.Slider(gui.Slider.INT)
        self._max_def_val.set_limits(0, 100)
        self._max_def_val.set_on_value_changed(self._on_max_def_value_change)
        self._max_def_val.double_value = self.max_displacement
        grid.add_child(self._max_def_val)

        grid.add_child(gui.Label('Smoothing'))
        self._smoothing = gui.Button("Enabled")
        self._smoothing.toggleable = True
        self._smoothing.is_on = self.smoothing
        self._smoothing.set_on_clicked(self._on_smoothing_change)
        grid.add_child(self._smoothing)

        rock_settings.add_child(grid)

        rock_settings.add_child(self._new_button)

        self.gui = rock_settings
        self.gui.visible = False

    def _on_dfactor_change(self, number):
        self.dfactor = number

    def _on_iter_change(self, number):
        self.iterations = int(number)

    def _on_seed_change(self, number):
        self.seed = int(number)

    def _on_smoothing_change(self):
        self.smoothing = self._smoothing.is_on
        if self._smoothing.is_on:
            self._smoothing.text = "Enabled"
        else:
            self._smoothing.text = "Disabled"

    def _on_min_def_value_change(self, number):
        self.min_displacement = int(number)

    def _on_max_def_value_change(self, number):
        self.max_displacement = int(number)

    def set_operation_number(self):
        self.max_operations_number = 2 * self.iterations + 2 + 1 * self.smoothing

    def generate(self):

        self.rng = np.random.default_rng(self.seed)

        print("Create base mesh")
        self.create_base_mesh()

        self.increment_and_display_operations()

        print("Randomize base mesh")
        self.randomize_mesh()
        self.increment_and_display_operations()

        dampening_factor = self.dfactor

        for i in range(self.iterations):
            print("Subdivision ", i + 1, "/", self.iterations)
            min_max = self.subdivise_middle_of_triangle()
            self.increment_and_display_operations()

            print("Displacment ", i + 1, "/", self.iterations)
            self.displace_vertices(min_max, dampening_factor)
            self.increment_and_display_operations()

            dampening_factor *= self.dfactor

        if self.smoothing:
            print("Smoothing")
            self.mesh = self.mesh.filter_smooth_laplacian(2)
            self.increment_and_display_operations()

    def subdivise_middle_of_triangle(self):
        vertices = np.asarray(self.mesh.vertices)
        triangles = np.asarray(self.mesh.triangles)
        number_vert = vertices.shape[0]

        new_vertices = np.zeros((int(vertices.shape[0] + triangles.shape[0] * 3), 3))
        new_vertices[:number_vert, :] = vertices
        new_triangles = np.zeros((triangles.shape[0] * 4, 3))

        i = 0
        j = number_vert

        for triangle in triangles:
            new_vertex = np.zeros((3, 3))
            new_vertex_index = np.zeros((3, 1)) - 1
            new_vertex[0] = (vertices[triangle[0]] + vertices[triangle[1]]) / 2
            new_vertex[1] = (vertices[triangle[1]] + vertices[triangle[2]]) / 2
            new_vertex[2] = (vertices[triangle[2]] + vertices[triangle[0]]) / 2

            k = 0

            for vertex in new_vertex:
                for index in range(j):
                    if np.array_equal(new_vertices[index], vertex):
                        new_vertex_index[k] = index
                if new_vertex_index[k] == -1:
                    new_vertex_index[k] = j
                    new_vertices[j] = vertex
                    j += 1
                k += 1

            new_triangles[i * 4] = [triangle[0], new_vertex_index[0], new_vertex_index[2]]
            new_triangles[i * 4 + 1] = [triangle[1], new_vertex_index[1], new_vertex_index[0]]
            new_triangles[i * 4 + 2] = [triangle[2], new_vertex_index[2], new_vertex_index[1]]
            new_triangles[i * 4 + 3] = [new_vertex_index[0], new_vertex_index[1], new_vertex_index[2]]
            i += 1

        self.mesh.vertices = o3d.utility.Vector3dVector(new_vertices[:j])
        self.mesh.triangles = o3d.utility.Vector3iVector(new_triangles)

        return number_vert, j

    def displace_vertices(self, min_max, d_factor):
        vertices = np.asarray(self.mesh.vertices)
        for i in range(min_max[0], min_max[1]):
            vertices[i] *= 1 + (
                    self.rng.uniform(-self.min_displacement, self.max_displacement) / 100) * d_factor
        self.mesh.vertices = o3d.utility.Vector3dVector(vertices)

    def randomize_mesh(self):
        vertices = np.asarray(self.mesh.vertices)
        for vertex in vertices:
            vertex *= self.rng.uniform(75, 150) / 100
        self.mesh.vertices = o3d.utility.Vector3dVector(vertices)
