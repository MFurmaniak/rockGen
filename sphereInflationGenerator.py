from generator import Generator
import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui


class SphereInflationGenerator(Generator):

    dfactor = 0
    iterations = 0
    min_displacement = 0
    max_displacement = 0

    def __init__(self, app_window):
        self.AppWindow = app_window
        em = app_window.window.theme.font_size
        rock_settings = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        rock_settings.add_child(gui.Label("Sphere Inflation Generator"))
        grid = gui.VGrid(2, 0.25*em)
        rock_settings.add_child(grid)
        grid.add_child(gui.Label("Subdivision iterations"))
        self._sub_iterations_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._sub_iterations_input.set_on_value_changed(self._on_iter_change)
        grid.add_child(self._sub_iterations_input)

        grid.add_child(gui.Label("Dampening factor"))
        self._dampening_factor = gui.Slider(gui.Slider.DOUBLE)
        self._dampening_factor.set_limits(0,1)
        self._dampening_factor.set_on_value_changed(self._on_dfactor_change)
        grid.add_child(self._dampening_factor)

        rock_settings.add_child(gui.Label("Deformation values"))
        grid = gui.VGrid(2, 0.25*em)

        grid.add_child(gui.Label("Minimal displacement"))
        self._min_def_val = gui.Slider(gui.Slider.INT)
        self._min_def_val.set_limits(-30, 100)
        self._min_def_val.set_on_value_changed(self._on_min_def_value_change)
        grid.add_child(self._min_def_val)

        grid.add_child(gui.Label("Maximum displacement"))
        self._max_def_val = gui.Slider(gui.Slider.INT)
        self._max_def_val.set_limits(0, 100)
        self._max_def_val.set_on_value_changed(self._on_max_def_value_change)
        grid.add_child(self._max_def_val)

        rock_settings.add_child(grid)

        self._new_button = gui.Button("Generate")
        self._new_button.set_on_clicked(self._on_menu_new)
        rock_settings.add_child(self._new_button)

        self.gui = rock_settings
        self.gui.visible = False

    def _on_dfactor_change(self,number):
        self.dfactor = number

    def _on_iter_change(self, number):
        self.iterations = int(number)

    def _on_min_def_value_change(self,number):
        self.min_displacement = int(number)

    def _on_max_def_value_change(self,number):
        self.max_displacement = int(number)

    def generate(self):
        self.mesh = o3d.geometry.TriangleMesh.create_icosahedron()

        self.randomize_mesh()
        dampening_factor = self.dfactor

        for i in range(self.iterations):
            min_max = self.subdivise_middle_of_triangle()
            self.displace_vertices(min_max, dampening_factor)
            dampening_factor *= self.dfactor

        self.mesh = self.mesh.filter_smooth_laplacian(2)
        o3d.io.write_triangle_mesh("dupa123.obj", self.mesh)
        gui.Application.instance.post_to_main_thread(self.AppWindow.window, self.AppWindow.display_mesh)

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
            vertices[i] *= 1 + (np.random.random_integers(-self.min_displacement, self.max_displacement) / 100) * d_factor
        self.mesh.vertices = o3d.utility.Vector3dVector(vertices)

    def randomize_mesh(self):
        vertices = np.asarray(self.mesh.vertices)
        for vertex in vertices:
            vertex *= np.random.random_integers(75, 150) / 100
        self.mesh.vertices = o3d.utility.Vector3dVector(vertices)
