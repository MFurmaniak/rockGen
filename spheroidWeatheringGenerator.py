from generator import Generator
import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
from modes import Modes


class SpheroidWeatheringGenerator(Generator):
    height = 40
    threshold = 0.02
    step = 0.1
    size_of_spheroid = 3
    filename = "rockmask6.png"
    weathering_panels = [None] * 5

    def __init__(self, app_window):

        self.AppWindow = app_window
        em = app_window.window.theme.font_size
        rock_settings = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        rock_settings.add_child((gui.Label("Spheroid Weathering Generator")))

        # todo gui
        #self._image = gui.ImageWidget()
        self._image_name = gui.Label(self.filename)
        self._image_open = gui.Button("Open")
        self._image_open.set_on_clicked(self._on_image_open)

        vert = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        grid = gui.VGrid(2, 0.5, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        #grid.add_child(self._image)
        grid.add_child(vert)

        vert.add_child(self._image_name)
        vert.add_child(self._image_open)

        rock_settings.add_child(grid)
        # todo change size of Image

        grid = gui.VGrid(2, 0.25 * em)

        grid.add_child(gui.Label("Height"))
        self._height_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._height_input.set_value(self.height)
        self._height_input.set_on_value_changed(self._on_height_change)
        grid.add_child(self._height_input)

        grid.add_child(gui.Label("Size of spheroid"))
        self._size_spheroid_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._size_spheroid_input.set_value(self.size_of_spheroid)
        self._size_spheroid_input.set_on_value_changed(self._on_size_spheroid_change)
        grid.add_child(self._size_spheroid_input)

        grid.add_child(gui.Label("Threshold"))
        self._threshold = gui.Slider(gui.Slider.DOUBLE)
        self._threshold.set_limits(0, 1)
        self._threshold.double_value = self.threshold
        self._threshold.set_on_value_changed(self._on_threshold_change)
        grid.add_child(self._threshold)

        grid.add_child(gui.Label("Step"))
        self._step = gui.Slider(gui.Slider.DOUBLE)
        self._step.set_limits(0, 1)
        self._step.double_value = self.step
        self._step.set_on_value_changed(self._on_step_change)
        grid.add_child(self._step)

        rock_settings.add_child(grid)

        self._new_button = gui.Button("Generate")
        self._new_button.set_on_clicked(self._on_menu_new)

        for i in range(5):
            self.weathering_panels[i] = WeatheringPanel(em)
            rock_settings.add_child(self.weathering_panels[i].gui)
        for i in range(4):
            self.weathering_panels[i].next = self.weathering_panels[i+1]

        rock_settings.add_child(self._new_button)

        self.gui = rock_settings
        self.gui.visible = False

    def _on_step_change(self, value):
        self.step = value

    def _on_threshold_change(self, value):
        self.threshold = value

    def _on_height_change(self, value):
        self.height = int(value)

    def _on_size_spheroid_change(self, value):
        self.size_of_spheroid = int(value)

    def _on_image_open(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load",
                             self.AppWindow.window.theme)
        dlg.add_filter(".png", "PNG")
        dlg.add_filter("", "All files")
        # A file dialog MUST define on_cancel and on_done functions
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        dlg.set_on_done(self._on_load_dialog_done)
        self.AppWindow.window.show_dialog(dlg)

    def _on_file_dialog_cancel(self):
        self.AppWindow.window.close_dialog()

    def _on_load_dialog_done(self, filename):
        self.AppWindow.window.close_dialog()
        self.filename = filename

    def generate(self):

        image_mask = o3d.io.read_image(self.filename)
        width = np.asarray(image_mask).shape[0]
        depth = np.asarray(image_mask).shape[1]

        levels = [[0, Modes.CAP, 0]] * 5

        for i in range(len(self.weathering_panels)):
            levels[i] = self.weathering_panels[i].level

        to_remove = []
        for level in levels:
            print(level)
            if level[0] <= 0.00001 or level[2] <= 0.00001:
                to_remove.append(level)
        for level in to_remove:
            levels.remove(level)

        points_life = np.zeros((width, self.height, depth))
        mask = np.asarray(image_mask)

        min_x = width
        min_z = depth
        max_x = 0
        max_z = 0

        x = 0

        numberofcolumns = 0

        for i in mask:
            z = 0
            for j in i:
                if (all(j)):
                    points_life[x, :, z] = 1
                    numberofcolumns += 1
                    if min_x > x:
                        min_x = x
                    if min_z > z:
                        min_z = z
                    if max_x < x:
                        max_x = x
                    if max_z < z:
                        max_z = z
                z += 1
            x += 1

        resistance_template = []
        for i in range(-self.size_of_spheroid - 1, self.size_of_spheroid + 1):
            for j in range(-self.size_of_spheroid - 1, self.size_of_spheroid + 1):
                for k in range(-self.size_of_spheroid - 1, self.size_of_spheroid + 1):
                    if 0 < np.abs(i) + np.abs(j) + np.abs(k) <= self.size_of_spheroid:
                        resistance_template += [[i, j, k]]
        resistance = -0.8 / (len(resistance_template))

        # resistance_template = [(1, 0, 0, -0.16), (-1, 0, 0, -0.16), (0, 0, 1, -0.16),
        #                        (0, 0, -1, -0.16), (0, -1, 0, -0.16), (0, 1, 0, -0.16), ]

        # todo parameters for all of the shapes

        top = self.height
        top_float = top
        print(levels)
        for level in levels:
            bottom_float = top_float - self.height * level[0]
            bottom = int(bottom_float)
            self.set_life(points_life[:, bottom:top, :], level[1])

            # main weathering loop

            for number_of_iteration in range(level[2]):
                points_resistances = np.ones((width, self.height, depth))

                for x in range(min_x, max_x + 1):
                    for z in range(min_z, max_z + 1):
                        for y in range(bottom, top):
                            if points_life[x, y, z] > self.threshold:
                                for i in resistance_template:
                                    if (0 < x + i[0] < width and 0 < y + i[1] < self.height and 0 < z + i[2] < depth):
                                        if (points_life[x + i[0], y + i[1], z + i[2]]) < self.threshold:
                                            points_resistances[x, y, z] += resistance
                                    else:
                                        points_resistances[x, y, z] += resistance
                points_life[:, bottom:top, :] -= (1 - points_resistances[:, bottom:top, :]) * self.step
                print(level, " ", number_of_iteration)
            top_float = bottom_float
            top = bottom

        # marching cube

        mesh = self.marching_cube(points_life, self.threshold)

        mesh.compute_vertex_normals()
        mesh = mesh.filter_smooth_laplacian(1)
        o3d.io.write_triangle_mesh("rock.obj", mesh)
        self.mesh = mesh
        gui.Application.instance.post_to_main_thread(self.AppWindow.window, self.AppWindow.display_mesh)

    def set_life(self, points_life, mode):

        width = points_life.shape[0]
        height = points_life.shape[1]
        depth = points_life.shape[2]

        if mode == Modes.HOURGLASS:
            for y in range(height):
                points_life[:, y, :] *= (np.abs(y - 0.5 * height) * 0.12 + 1)
        if mode == Modes.ROUND:
            for x in range(width):
                for z in range(depth):
                    points_life[x, :, z] *= 0.5 * (width - np.abs(x - 0.5 * width)) \
                                            / (0.5 * width) * (depth - np.abs(z - 0.5 * depth)) / (0.5 * depth)
        if mode == Modes.CAP:
            for y in range(height):
                points_life[:, y, :] *= 1 + (1 - y / height)
            for x in range(width):
                for z in range(depth):
                    points_life[x, :, z] *= 0.2 * ((width - np.abs(x - 0.5 * width)) /
                                                   (0.5 * width)) * ((depth - np.abs(z - 0.5 * depth)) / (0.5 * depth))
        if mode == Modes.BARREL:
            for y in range(height):
                points_life[:, y, :] *= ((height - np.abs(y - 0.5 * height)) * 0.1)

    def marching_cube(self, points_life, threshold):
        shape = points_life.shape
        width = shape[0]
        height = shape[1]
        depth = shape[2]

        points_life_copy = np.zeros((width + 2, height + 2, depth + 2))

        points_life_copy[1:width + 1, 1:height + 1, 1:depth + 1] = points_life
        points_life = points_life_copy

        vertices_temp = np.asarray([[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 2, 10, 0, 2, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 8, 3, 2, 10, 8, 10, 9, 8, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 11, 2, 8, 11, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 9, 0, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 11, 2, 1, 9, 11, 9, 8, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 10, 1, 11, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 10, 1, 0, 8, 10, 8, 11, 10, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 9, 0, 3, 11, 9, 11, 10, 9, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 3, 0, 7, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 10, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 4, 7, 3, 0, 4, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 2, 10, 9, 0, 2, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1, -1, -1, -1],
                                    [8, 4, 7, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [11, 4, 7, 11, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 0, 1, 8, 4, 7, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1, -1, -1, -1],
                                    [3, 10, 1, 3, 11, 10, 7, 8, 4, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1, -1, -1, -1],
                                    [4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1, -1, -1, -1],
                                    [4, 7, 11, 4, 11, 9, 9, 11, 10, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 5, 4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 10, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 0, 8, 1, 2, 10, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 2, 10, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, -1],
                                    [9, 5, 4, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 11, 2, 0, 8, 11, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 5, 4, 0, 1, 5, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1, -1, -1, -1],
                                    [10, 3, 11, 10, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1, -1, -1, -1],
                                    [5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1, -1, -1, -1],
                                    [5, 4, 8, 5, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 3, 0, 9, 5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 7, 8, 0, 1, 7, 1, 5, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 7, 8, 9, 5, 7, 10, 1, 2, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, -1],
                                    [8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1, -1, -1, -1],
                                    [2, 10, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [7, 9, 5, 7, 8, 9, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1, -1, -1, -1],
                                    [2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1, -1, -1, -1],
                                    [11, 2, 1, 11, 1, 7, 7, 1, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1, -1, -1, -1],
                                    [5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1],
                                    [11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1],
                                    [11, 10, 5, 7, 11, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 3, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 0, 1, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 8, 3, 1, 9, 8, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 6, 5, 2, 6, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, -1],
                                    [2, 3, 11, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [11, 0, 8, 11, 2, 0, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 1, 9, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1, -1, -1, -1],
                                    [6, 3, 11, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1, -1, -1, -1],
                                    [3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1, -1, -1, -1],
                                    [6, 5, 9, 6, 9, 11, 11, 9, 8, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 10, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 3, 0, 4, 7, 3, 6, 5, 10, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 9, 0, 5, 10, 6, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1, -1, -1, -1],
                                    [6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, -1],
                                    [8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1, -1, -1, -1],
                                    [7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1],
                                    [3, 11, 2, 7, 8, 4, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1, -1, -1, -1],
                                    [0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1],
                                    [9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1],
                                    [8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1, -1, -1, -1],
                                    [5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1],
                                    [0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1],
                                    [6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1, -1, -1, -1],
                                    [10, 4, 9, 6, 4, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 10, 6, 4, 9, 10, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 0, 1, 10, 6, 0, 6, 4, 0, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1, -1, -1, -1],
                                    [1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, -1],
                                    [0, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 4, 9, 10, 6, 4, 11, 2, 3, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1, -1, -1, -1],
                                    [3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1, -1, -1, -1],
                                    [6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1],
                                    [9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1, -1, -1, -1],
                                    [8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1],
                                    [3, 11, 6, 3, 6, 0, 0, 6, 4, -1, -1, -1, -1, -1, -1, -1],
                                    [6, 4, 8, 11, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [7, 10, 6, 7, 8, 10, 8, 9, 10, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1, -1, -1, -1],
                                    [10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, -1],
                                    [10, 6, 7, 10, 7, 1, 1, 7, 3, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1, -1, -1, -1],
                                    [2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1],
                                    [7, 8, 0, 7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, -1],
                                    [7, 3, 2, 6, 7, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1, -1, -1, -1],
                                    [2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1],
                                    [1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1],
                                    [11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1, -1, -1, -1],
                                    [8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1],
                                    [0, 9, 1, 11, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1, -1, -1, -1],
                                    [7, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 0, 8, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 1, 9, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 1, 9, 8, 3, 1, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 1, 2, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 10, 3, 0, 8, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 9, 0, 2, 10, 9, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1, -1, -1, -1],
                                    [7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [7, 0, 8, 7, 6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 7, 6, 2, 3, 7, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1, -1, -1],
                                    [10, 7, 6, 10, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1, -1, -1, -1],
                                    [0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1, -1, -1, -1],
                                    [7, 6, 10, 7, 10, 8, 8, 10, 9, -1, -1, -1, -1, -1, -1, -1],
                                    [6, 8, 4, 11, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 6, 11, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 6, 11, 8, 4, 6, 9, 0, 1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1, -1, -1, -1],
                                    [6, 8, 4, 6, 11, 8, 2, 10, 1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1, -1, -1, -1],
                                    [4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1, -1, -1, -1],
                                    [10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1],
                                    [8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, -1],
                                    [1, 9, 4, 1, 4, 2, 2, 4, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1, -1, -1, -1],
                                    [10, 1, 0, 10, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1],
                                    [10, 9, 4, 6, 10, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 9, 5, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 3, 4, 9, 5, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 0, 1, 5, 4, 0, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, -1],
                                    [9, 5, 4, 10, 1, 2, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1, -1, -1, -1],
                                    [7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1, -1, -1, -1],
                                    [3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1],
                                    [7, 2, 3, 7, 6, 2, 5, 4, 9, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1, -1, -1],
                                    [3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, -1],
                                    [6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1],
                                    [9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1, -1, -1, -1],
                                    [1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1],
                                    [4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1],
                                    [7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1, -1, -1, -1],
                                    [6, 9, 5, 6, 11, 9, 11, 8, 9, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, -1],
                                    [0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1, -1, -1, -1],
                                    [6, 11, 3, 6, 3, 5, 5, 3, 1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1, -1, -1, -1],
                                    [0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1],
                                    [11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1],
                                    [6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1, -1, -1, -1],
                                    [5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1, -1, -1, -1],
                                    [9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1],
                                    [1, 5, 6, 2, 1, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1],
                                    [10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, -1],
                                    [0, 3, 8, 5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 5, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [11, 5, 10, 7, 5, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [11, 5, 10, 11, 7, 5, 8, 3, 0, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 11, 7, 5, 10, 11, 1, 9, 0, -1, -1, -1, -1, -1, -1, -1],
                                    [10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, -1],
                                    [11, 1, 2, 11, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1, -1, -1, -1],
                                    [9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1, -1, -1, -1],
                                    [7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1],
                                    [2, 5, 10, 2, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1, -1, -1, -1],
                                    [9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1, -1, -1, -1],
                                    [9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1],
                                    [1, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 7, 0, 7, 1, 1, 7, 5, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 8, 4, 5, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1],
                                    [5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1, -1, -1, -1],
                                    [0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1, -1, -1, -1],
                                    [10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1],
                                    [2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1, -1, -1, -1],
                                    [0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1],
                                    [0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1],
                                    [9, 4, 5, 2, 11, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, -1],
                                    [5, 10, 2, 5, 2, 4, 4, 2, 0, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1],
                                    [5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, -1],
                                    [8, 4, 5, 8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 4, 5, 1, 0, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1, -1, -1, -1],
                                    [9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 11, 7, 4, 9, 11, 9, 10, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1, -1, -1, -1],
                                    [1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1, -1, -1, -1],
                                    [3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1],
                                    [4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1, -1, -1, -1],
                                    [9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1],
                                    [11, 7, 4, 11, 4, 2, 2, 4, 0, -1, -1, -1, -1, -1, -1, -1],
                                    [11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1, -1, -1, -1],
                                    [2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, -1],
                                    [9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1],
                                    [3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1],
                                    [1, 10, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, -1],
                                    [4, 0, 3, 7, 4, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [4, 8, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 0, 9, 3, 9, 11, 11, 9, 10, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 1, 10, 0, 10, 8, 8, 10, 11, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 1, 10, 11, 3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 2, 11, 1, 11, 9, 9, 11, 8, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1, -1, -1, -1],
                                    [0, 2, 11, 8, 0, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [3, 2, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 3, 8, 2, 8, 10, 10, 8, 9, -1, -1, -1, -1, -1, -1, -1],
                                    [9, 10, 2, 0, 9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1, -1, -1, -1],
                                    [1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [0, 3, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]])
        triangle_list = np.zeros(shape=(width * height * depth * 3, 3))
        vertices_list = np.zeros(shape=(width * height * depth * 3, 3))
        number_of_vertices = 0
        number_of_triangles = 0
        for x in range(0, width + 1):
            for z in range(0, depth + 1):
                for y in range(0, height):
                    cube_value = 0
                    cube_vertices = np.array(
                        [[x, y, z + 1], [x + 1, y, z + 1],
                         [x + 1, y, z], [x, y, z],
                         [x, y + 1, z + 1],
                         [x + 1, y + 1, z + 1],
                         [x + 1, y + 1, z],
                         [x, y + 1, z]])

                    if z + 1 < depth and x < width and y < height and points_life[
                        x, y, z + 1] > threshold: cube_value += 1  # 0
                    if x + 1 < width and z + 1 < depth and points_life[
                        x + 1, y, z + 1] > threshold: cube_value += 2  # 1
                    if x + 1 < width and points_life[x + 1, y, z] > threshold: cube_value += 4  # 2
                    if points_life[x, y, z] > threshold: cube_value += 8  # 3
                    if y + 1 < height and z + 1 < depth and points_life[
                        x, y + 1, z + 1] > threshold: cube_value += 16  # 4
                    if y + 1 < height and z + 1 < depth and points_life[
                        x + 1, y + 1, z + 1] > threshold: cube_value += 32  # 5
                    if y + 1 < height and x + 1 < width and points_life[
                        x + 1, y + 1, z] > threshold: cube_value += 64  # 6
                    if y + 1 < height and points_life[
                        x, y + 1, z] > threshold: cube_value += 128  # 7

                    vertices_cords = np.asarray(
                        [self.interpolation(cube_vertices[0], cube_vertices[1],
                                            points_life[cube_vertices[0, 0], cube_vertices[0, 1], cube_vertices[0, 2]],
                                            points_life[cube_vertices[1, 0], cube_vertices[1, 1], cube_vertices[1, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[1], cube_vertices[2],
                                            points_life[cube_vertices[1, 0], cube_vertices[1, 1], cube_vertices[1, 2]],
                                            points_life[cube_vertices[2, 0], cube_vertices[2, 1], cube_vertices[2, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[2], cube_vertices[3],
                                            points_life[cube_vertices[2, 0], cube_vertices[2, 1], cube_vertices[2, 2]],
                                            points_life[cube_vertices[3, 0], cube_vertices[3, 1], cube_vertices[3, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[3], cube_vertices[0],
                                            points_life[cube_vertices[3, 0], cube_vertices[3, 1], cube_vertices[3, 2]],
                                            points_life[cube_vertices[0, 0], cube_vertices[0, 1], cube_vertices[0, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[4], cube_vertices[5],
                                            points_life[cube_vertices[4, 0], cube_vertices[4, 1], cube_vertices[4, 2]],
                                            points_life[cube_vertices[5, 0], cube_vertices[5, 1], cube_vertices[5, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[5], cube_vertices[6],
                                            points_life[cube_vertices[5, 0], cube_vertices[5, 1], cube_vertices[5, 2]],
                                            points_life[cube_vertices[6, 0], cube_vertices[6, 1], cube_vertices[6, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[6], cube_vertices[7],
                                            points_life[cube_vertices[6, 0], cube_vertices[6, 1], cube_vertices[6, 2]],
                                            points_life[cube_vertices[7, 0], cube_vertices[7, 1], cube_vertices[7, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[7], cube_vertices[4],
                                            points_life[cube_vertices[7, 0], cube_vertices[7, 1], cube_vertices[7, 2]],
                                            points_life[cube_vertices[4, 0], cube_vertices[4, 1], cube_vertices[4, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[0], cube_vertices[4],
                                            points_life[cube_vertices[0, 0], cube_vertices[0, 1], cube_vertices[0, 2]],
                                            points_life[cube_vertices[4, 0], cube_vertices[4, 1], cube_vertices[4, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[1], cube_vertices[5],
                                            points_life[cube_vertices[1, 0], cube_vertices[1, 1], cube_vertices[1, 2]],
                                            points_life[cube_vertices[5, 0], cube_vertices[5, 1], cube_vertices[5, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[2], cube_vertices[6],
                                            points_life[cube_vertices[2, 0], cube_vertices[2, 1], cube_vertices[2, 2]],
                                            points_life[cube_vertices[6, 0], cube_vertices[6, 1], cube_vertices[6, 2]],
                                            threshold),
                         self.interpolation(cube_vertices[3], cube_vertices[7],
                                            points_life[cube_vertices[3, 0], cube_vertices[3, 1], cube_vertices[3, 2]],
                                            points_life[cube_vertices[7, 0], cube_vertices[7, 1], cube_vertices[7, 2]],
                                            threshold)])

                    vertices_index = np.zeros(12) - 1
                    counter = 0
                    for i in vertices_temp[cube_value]:
                        if i != -1:
                            if vertices_index[i] == -1:
                                vertices_list[number_of_vertices] = vertices_cords[i]
                                vertices_index[i] = number_of_vertices
                                number_of_vertices += 1
                            if counter % 3 == 2:
                                triangle_list[number_of_triangles] = [
                                    vertices_index[vertices_temp[cube_value, counter - 2]],
                                    vertices_index[vertices_temp[cube_value, counter - 1]],
                                    vertices_index[vertices_temp[cube_value, counter]]]
                                number_of_triangles += 1
                            counter += 1
                        else:
                            break
        mesh = o3d.geometry.TriangleMesh()
        list_of_points = vertices_list[:number_of_vertices] - (0.5 * width + 2, 0.5 * height + 2, 0.5 * depth + 2)
        list_of_triangles = triangle_list[:number_of_triangles]
        mesh.vertices = o3d.utility.Vector3dVector(list_of_points)
        list_of_triangles = list_of_triangles[:, [1, 0, 2]]
        mesh.triangles = o3d.utility.Vector3iVector(list_of_triangles)
        mesh.remove_duplicated_vertices()
        mesh.merge_close_vertices(1)
        mesh.remove_degenerate_triangles()
        mesh.remove_non_manifold_edges()
        return mesh

    def interpolation(self, p1, p2, v1, v2, threshold):
        if np.abs(threshold - v1) < 0.00001:
            return p1
        if np.abs(threshold - v2) < 0.00001:
            return p2
        if np.abs(v1 - v2) < 0.00001:
            return p1
        mu = ((threshold - v1) / (v2 - v1))
        if mu > 1:
            mu = 1
        return p1 + (p2 - p1) * mu




class WeatheringPanel:

    def __init__(self, em):
        self.next = None
        self.max = 1
        self.level = [0, Modes.CAP, 0]
        self.gui = gui.Vert(0, gui.Margins(0.25 * em))
        grid2 = gui.VGrid(2, 0.25 * em)
        self._percent = gui.Slider(gui.Slider.DOUBLE)
        self._percent.set_limits(0, self.max)
        self._percent.set_on_value_changed(self._on_percent)

        _iterations_input = gui.NumberEdit(gui.NumberEdit.Type.INT)
        _iterations_input.set_on_value_changed(self._on_iterations)

        _mode = gui.Combobox()
        _mode.add_item("Cap")
        _mode.add_item("Barrel")
        _mode.add_item("Hourglass")
        _mode.add_item("Round")

        _mode.set_on_selection_changed(self._on_mode)

        grid2.add_child((gui.Label("Mode")))
        grid2.add_child(_mode)
        grid2.add_child((gui.Label("Iterations")))
        grid2.add_child(_iterations_input)
        grid2.add_child((gui.Label("Percent of height")))
        grid2.add_child(self._percent)

        self.gui.add_child(grid2)

    def _on_mode(self, text, index):
        if index == 0:
            self.level[1] = Modes.CAP
        if index == 1:
            self.level[1] = Modes.BARREL
        if index == 2:
            self.level[1] = Modes.HOURGLASS
        if index == 3:
            self.level[1] = Modes.ROUND

    def _on_iterations(self, number):
        self.level[2] = int(number)

    def _on_percent(self, number):
        self.level[0] = number
        if self.next is not None:
            self.next._set_max(self.max - self.level[0])

    def _set_max(self, max):
        if (max < 0):
            max = 0
        self.max = max
        self._percent.set_limits(0, max)
        if self.level[0] > self.max:
            self.level[0] = self.max

        if self.next is not None:
            self.next._set_max(self.max - self.level[0])
