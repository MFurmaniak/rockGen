from generator import Generator
import open3d.visualization.gui as gui
import numpy as np
import open3d as o3d
import noise

class SimpleNoiseGenerator(Generator):
    # Rock Settings
    seed = 0
    mesh_radius = 1
    mesh_scale = 10
    cuts_number = 20
    number_of_iterations = 3
    low_cut = 0.6
    high_cut = 0.7
    noise_number_of_octaves = 8
    noise_str = 2
    noise_offset = 1
    mesh = None
    rock_settings = None

    def __init__(self, app_window):
        super().__init__(app_window)
        em = app_window.window.theme.font_size
        rock_settings = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        rock_settings.add_child((gui.Label("Simple Noise Generator")))
        grid = gui.VGrid(2, 0 * em)
        grid.add_child(gui.Label("Seed"))
        self._seed_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._seed_input.set_value(self.seed)
        self._seed_input.set_on_value_changed(self._on_seed_change)
        grid.add_child(self._seed_input)

        grid.add_child(gui.Label("Mesh radius"))
        self._mesh_radius_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._mesh_radius_input.set_value(self.mesh_radius)
        self._mesh_radius_input.set_on_value_changed(self._on_mesh_radius_change)
        grid.add_child(self._mesh_radius_input)

        grid.add_child(gui.Label("Mesh scale"))
        self._mesh_scale_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._mesh_scale_input.set_value(self.mesh_scale)
        self._mesh_scale_input.set_on_value_changed(self._on_mesh_scale_change)
        grid.add_child(self._mesh_scale_input)

        rock_settings.add_child(grid)
        grid = gui.VGrid(2, 0 * em)

        grid.add_child(gui.Label("Subdivision iterations"))
        self._subdivision_iterations_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._subdivision_iterations_input.set_value(self.number_of_iterations)
        self._subdivision_iterations_input.set_on_value_changed(self._on_subdivision_iterations_change)
        grid.add_child(self._subdivision_iterations_input)

        rock_settings.add_child(grid)
        grid = gui.VGrid(2, 0 * em)

        grid.add_child(gui.Label("Number of cuts"))
        self._cuts_number_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._cuts_number_input.set_value(self.cuts_number)
        self._cuts_number_input.set_on_value_changed(self._on_cuts_number_change)
        grid.add_child(self._cuts_number_input)

        grid.add_child(gui.Label("Minimal cut"))
        self._low_cut = gui.Slider(gui.Slider.DOUBLE)
        self._low_cut.set_limits(0, 1)
        self._low_cut.double_value = self.low_cut
        self._low_cut.set_on_value_changed(self._on_low_cut_change)
        grid.add_child(self._low_cut)

        grid.add_child(gui.Label("Maximum cut"))
        self._high_cut = gui.Slider(gui.Slider.DOUBLE)
        self._high_cut.set_limits(0, 1)
        self._high_cut.double_value = self.high_cut
        self._high_cut.set_on_value_changed(self._on_high_cut_change)
        grid.add_child(self._high_cut)

        rock_settings.add_child(grid)
        grid = gui.VGrid(2, 0 * em)

        grid.add_child(gui.Label("Noise Octaves"))
        self._noise_octaves_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._noise_octaves_input.set_value(self.noise_number_of_octaves)
        self._noise_octaves_input.set_on_value_changed(self._on_noise_octaves_change)
        grid.add_child(self._noise_octaves_input)

        grid.add_child(gui.Label("Noise strength"))
        self._noise_str_input = gui.NumberEdit(gui.NumberEdit.Type.DOUBLE)
        self._noise_str_input.set_value(self.noise_str)
        self._noise_str_input.set_on_value_changed(self._on_noise_str_change)
        grid.add_child(self._noise_str_input)

        grid.add_child(gui.Label("Noise offset"))
        self._noise_offset_input = gui.NumberEdit(gui.NumberEdit.Type.DOUBLE)
        self._noise_offset_input.set_value(self.noise_offset)
        self._noise_offset_input.set_on_value_changed(self._on_noise_offset_change)
        grid.add_child(self._noise_offset_input)

        rock_settings.add_child(grid)

        rock_settings.add_child(self._new_button)

        self.gui = rock_settings

    def _on_seed_change(self, seed):
        self.seed = int(seed)

    def _on_cuts_number_change(self, number):
        self.cuts_number = int(number)

    def _on_mesh_radius_change(self, number):
        self.mesh_radius = int(number)

    def _on_mesh_scale_change(self, number):
        self.mesh_scale = number

    def _on_subdivision_iterations_change(self, number):
        self.number_of_iterations = int(number)

    def _on_noise_octaves_change(self, number):
        self.noise_number_of_octaves = int(number)

    def _on_noise_offset_change(self, number):
        self.noise_offset = number

    def _on_noise_str_change(self, number):
        self.noise_str = number

    def _on_low_cut_change(self, number):
        self.low_cut = number

    def _on_high_cut_change(self, number):
        self.high_cut = number

    def set_operation_number(self):
        self.max_operations_number = 5

    def generate(self):

        rng = np.random.default_rng(self.seed)

        mesh = o3d.geometry.TriangleMesh.create_octahedron(radius=self.mesh_radius)
        self.increment_and_display_operations()

        mesh = mesh.subdivide_loop(number_of_iterations=self.number_of_iterations)
        self.increment_and_display_operations()

        vertices = np.asarray(mesh.vertices)
        d = rng.uniform(low=self.low_cut, high=self.high_cut) * self.mesh_radius
        if self.cuts_number > 0:
            for i in range(self.cuts_number):
                rotation = mesh.get_rotation_matrix_from_xyz(
                    (np.pi / rng.uniform(low=0.5, high=4), 0, np.pi / rng.uniform(low=0.5, high=4)))
                mesh.rotate(rotation, center=(0, 0, 0))
                for j in range(vertices.shape[0]):
                    if vertices[j][1] > d:
                        vertices[j][1] = d
        self.increment_and_display_operations()

        for i in range(vertices.shape[0]):
            noise_value = noise.pnoise3(vertices[i][0], vertices[i][1], vertices[i][2] + self.noise_offset,
                                        octaves=self.noise_number_of_octaves)
            vertices[i] *= (1 + noise_value * self.noise_str)
        self.increment_and_display_operations()

        mesh.scale(self.mesh_scale, center=[0, 0, 0])
        self.increment_and_display_operations()

        mesh.vertices = o3d.utility.Vector3dVector(vertices)

        mesh.compute_vertex_normals()

        o3d.io.write_triangle_mesh("rock.obj", mesh)
        self.mesh = mesh
