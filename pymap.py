#!/usr/bin/env python.
# -*- coding: utf-8 -*-
''''''
#########################################################################
#                                                                       #
#                             Backend code                              #
#                                                                       #
#########################################################################

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class Polygon:
    '''This object holds the shape to be plotted in the plot window.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        self.array = np.stack((x_list, y_list))
        self.name = name


class Matrix(Polygon):
    '''This object holds the matrix to be used when transforming the shape.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        super().__init__(name, x_list, y_list)


class BasePoint:
    '''This should be replaced by a function.'''
    def __init__(self, x=0, y=0):
        self.array = np.array((x, y))
        self.array.shape = (2, 1)


class AppData:
    '''Gathers all of the backend calculations into a single object.'''
    def __init__(self, polygon_name=None, matrix_name=None, base_point=None):
        self.polygon_dict = _read_polygons_to_dict()
        self.matrix_dict = _read_matrices_to_dict()
        self.polygon = self.polygon_dict[polygon_name]
        self.matrix = self.matrix_dict[matrix_name]
        self.base_point = base_point
        self.make_plot_polygon()
        self.make_transformed_polygon()

    def make_plot_polygon(self):
        '''Create the untransformed polygon array for plotting.'''
        self.before = self.polygon.array + self.base_point.array

    def make_transformed_polygon(self):
        '''Create the transformed polygon array for plotting.'''
        self.after = self.matrix.array @ self.before


def _read_matrices_to_dict():
    '''Gets the list of matrices from the matrices.ini file.'''
    try:
        matrix_file = open("matrices.ini", "r")
    except FileNotFoundError:
        _renew_matrices_ini()
        matrix_file = open("matrices.ini", "r")
    matrix_data = matrix_file.read()
    matrix_file.close()
    matrix_data = matrix_data.split("\n")
    matrix_data = [s for s in matrix_data if s.strip() != "" and s[0] != '#']
    matrix_dict = dict()
    for data_string in matrix_data:
        if data_string.split(":")[0] == "name":
            name = data_string.split(":")[1]
            coeff_list = matrix_data[matrix_data.index(
                data_string) + 1].split(" ")
            coeff_list = [float(entry) for entry in coeff_list]
            matrix_dict[name] = Matrix(name, coeff_list[0:2], coeff_list[2:])
    return matrix_dict


def _renew_matrices_ini():
    '''Erases matrices.ini and replaces it with the default matrices.ini
    file.
    '''
    matrix_file = open('matrices.ini', 'w+')
    matrices_text = ["name:default\n0 1 -1 0\n\n",
                     "name:contracting rotation\n0.3 0.8 -0.8 0.3\n\n",
                     "name:expanding rotation\n0.9 0.7 -0.7 0.9\n\n",
                     "name:real eigenvalues\n0.2 -1.8 -1.2 0.8\n"]
    for data_string in matrices_text:
        matrix_file.write(data_string)
    matrix_file.close()


def _read_polygons_to_dict():
    '''Gets the list of polygons from the polygons.ini file.'''
    try:
        polygon_file = open("polygons.ini", "r")
    except FileNotFoundError:
        _renew_polygons_ini()
        polygon_file = open("polygons.ini", "r")
    polygon_data = polygon_file.read()
    polygon_file.close()
    polygon_data = polygon_data.split("\n")
    polygon_data = [data_string for data_string in polygon_data
                    if data_string.strip() != "" and data_string[0] != '#']
    polygon_dict = dict()
    for data_string in polygon_data:
        if data_string.split(":")[0] == "name":
            name = data_string.split(":")[1]
            coord_list = [0]*2
            for i in range(2):
                coord_list[i] = polygon_data[polygon_data.index(data_string)
                                             + 1 + i].split(" ")
                shift = float(coord_list[i].pop(0).split(":")[1])
                coord_list[i] = [float(entry) - shift for
                                 entry in coord_list[i]]
            polygon_dict[name] = Polygon(name, coord_list[0], coord_list[1])
    return polygon_dict


def _renew_polygons_ini():
    '''Erases polygons.ini and replaces it with the default polygon.ini
    file.
    '''
    polygon_file = open('polygons.ini', 'w+')
    polygons_text = ["name:rectangle\nx:0 0 2 2 0 0\ny:0 0 0 1 1 0\n\n",
                     "name:line\nx:0 0 1.7 0\ny:0 0 0.3 0\n\n",
                     "name:basis\nx:0 0 0 0 1 0\ny:0 0 1 0 0 0\n\n",
                     "name:square\nx:0 0 1 1 0 0\ny:0 0 0 1 1 0\n\n",
                     "name:dogegon\nx:1.3850 0.8711 1.0166 1.1751 1.7441 ",
                     "2.0674 1.9413 1.8443 1.7861 1.7279 1.2818 1.1977 ",
                     "1.1686 1.0490 1.0360 0.8679 0.8711\ny:1.4246 1.6176 ",
                     "1.8261 1.6097 1.5595 1.4302 1.3378 1.3378 1.0422 ",
                     "1.3326 1.3378 1.0106 1.3194 1.4012 1.5886 1.6176 "
                     "1.6176\n\n"]
    for data_string in polygons_text:
        polygon_file.write(data_string)
    polygon_file.close()

#########################################################################
#                                                                       #
#                             Tkinter code                              #
#                                                                       #
#########################################################################


app_data = AppData("rectangle", "default", BasePoint(.5, .5))


class SimpleFrame(tk.Frame):  # pylint: disable=too-many-ancestors
    '''This class is to condense some Frame creation and packing code into
    fewer lines.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, None)
        self.pack(*args, **kwargs)


class BufferFrame:
    """Empty frame for spacing purposes."""
    def __init__(self, parent, ht, wd, sd):
        self.container = tk.Frame(parent, height=ht, width=wd)
        self.container.pack(side=sd, expand=False)


class PyMapApp(tk.Tk):
    '''This is the main tkinter application.  Some documentation will
    go here.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().title("PyMap")
        self.container = SimpleFrame(self, side="top", fill="both",
                                     expand=True)
        # self.console_frame = BufferFrame(self.container, 20, 1, "top")
        # self.console = tk.Label(self.console_frame.container, text=\
        #                         "Please select a polygon" +\
        #                         " to transform.", font=("Courier", 12))
        # self.console.pack(side="top")
        self.main_frame = MainFrame(self.container)

    def replot(self):
        '''Currently just an alias.'''
        self.main_frame.plot_frame.replot()


class MainFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''Temporary class to help organize code.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.control_frame = ControlFrame(self, side="left",
                                          fill="none", expand=True)
        self.plot_frame = PlotFrame(self, side="left", fill="both",
                                    expand=True)


class ControlFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''Frame to house user controls.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        BufferFrame(self, 40, 1, "top")
        self.polygon_frame = PolygonFrame(self, side="top", fill="both",
                                          expand=True)
        BufferFrame(self, 10, 1, "top")
        self.base_point_frame = BasePointFrame(self, side="top", fill="both",
                                               expand=True)
        BufferFrame(self, 30, 1, "top")
        self.matrix_frame = MatrixFrame(self, side="top", fill="both",
                                        expand=True)
        BufferFrame(self, 300, 1, "top")

    def refresh_entries(self):
        '''This takes the data from app_data and propagates it to the UI.'''
        base_point = app_data.base_point.array
        self.base_point_frame.entry.ent_1.set(float(base_point.item(0, 0)))
        self.base_point_frame.entry.ent_2.set(float(base_point.item(1, 0)))
        array = app_data.matrix.array
        self.matrix_frame.row_1.ent_1.set(array.item(0, 0))
        self.matrix_frame.row_1.ent_2.set(array.item(0, 1))
        self.matrix_frame.row_2.ent_1.set(array.item(1, 0))
        self.matrix_frame.row_2.ent_2.set(array.item(1, 1))
        name = app_data.matrix.name
        self.matrix_frame.save_frame.matrix_name.set(name)
        app_data.make_plot_polygon()
        app_data.make_transformed_polygon()
        app.replot()

    def update_app_data(self):
        '''This takes the data from the UI and propagates it to app_data.'''
        base_point = BasePoint(self.base_point_frame.entry.ent_1.get(),
                               self.base_point_frame.entry.ent_2.get())
        app_data.base_point = base_point
        x_list = [self.matrix_frame.row_1.ent_1.get(),
                  self.matrix_frame.row_1.ent_2.get()]
        y_list = [self.matrix_frame.row_2.ent_1.get(),
                  self.matrix_frame.row_2.ent_2.get()]
        name = self.matrix_frame.save_frame.matrix_name.get()
        matrix = Matrix(name, x_list, y_list)
        if name not in list(app_data.matrix_dict.keys()):
            app_data.matrix_dict[name] = matrix
            self.matrix_frame.choices.append(name)
            self.matrix_frame.choice.set(name)
            self.matrix_frame.menu_frame.reload(
                self.matrix_frame.choice,
                *self.matrix_frame.choices,
                command=self.matrix_frame.change_matrix
                )
        app_data.matrix = matrix
        self.refresh_entries()
        app.replot()


class PolygonFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''A frame to hold polygon-related widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(self, text="Polygon Name",
                              font=("Helvetica", 12))
        self.label.pack(side="top")
        self.choice = tk.StringVar(self)
        self.choices = list(app_data.polygon_dict.keys())
        self.choice.set(self.choices[0])
        self.menu_frame = MenuFrame(self, self.choice, *self.choices,
                                    command=self.change_polygon)

    def change_polygon(self, choice):
        '''Changes the polygon in app_data when a new selection on the
        pulldown is made.  It then updates the rest of the UI.
        '''
        app_data.polygon = app_data.polygon_dict[choice]
        base_point = BasePoint(
            app.main_frame.control_frame.base_point_frame.entry.ent_1.get(),
            app.main_frame.control_frame.base_point_frame.entry.ent_2.get()
            )
        app_data.base_point = base_point
        app.main_frame.control_frame.refresh_entries()


class MenuFrame(tk.Frame):  # pylint: disable=too-many-ancestors
    '''Constructs a frame with a dropdown menu and a method to reload it.
    Tkinter does not make it easy to change the options on a dropdown menu,
    so this is my workaround.'''
    def __init__(self, parent, choice, *choices, command=None):
        super().__init__(parent)
        self.pack(side="top", fill="none", expand=True)
        if command is None:
            self.menu = tk.OptionMenu(self, choice, *choices)
        else:
            self.menu = tk.OptionMenu(self, choice, *choices, command=command)
        self.menu.config(width=20, height=1)
        self.menu.pack(side="top", fill="x", expand=True)

    def reload(self, choice, *choices, command=None):
        '''Recreates the pulldown menu with an updated options list.'''
        if hasattr(self, "menu"):
            self.menu.destroy()
        if command is None:
            self.menu = tk.OptionMenu(self, choice, *choices)
        else:
            self.menu = tk.OptionMenu(self, choice, *choices, command=command)
        self.menu.config(width=20, height=1)
        self.menu.pack(side="top", fill="x", expand=True)


class BasePointFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''Temporary class to help organize code.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(self, text="Translate the polygon by",
                              font=("Helvetica", 12))
        self.label.pack(side="top")
        self.entry = EntryFrame(self, side="top", fill="x", expand=True)


class MatrixFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''A frame to hold matrix-related widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(self, text="Matrix name", font=("Helvetica", 12))
        self.label.pack(side="top")
        self.choice = tk.StringVar(self)
        self.choices = list(app_data.matrix_dict.keys())
        self.choice.set(self.choices[0])
        self.menu_frame = MenuFrame(self, self.choice, *self.choices,
                                    command=self.change_matrix)
        BufferFrame(self, 10, 1, "top")
        self.label = tk.Label(self, text="Matrix entries",
                              font=("Helvetica", 12))
        self.label.pack(side="top")
        self.row_1 = EntryFrame(self, side="top", fill="x", expand=True)
        self.row_2 = EntryFrame(self, side="top", fill="x", expand=True)
        BufferFrame(self, 10, 1, "top")
        self.save_frame = SaveFrame(self, side="top", fill="both",
                                    expand=True)

    def change_matrix(self, choice):
        '''Changes the matrix in app_data when a new selection on the
        pulldown is made.  It then updates the rest of the UI.
        '''
        app_data.matrix = app_data.matrix_dict[choice]
        base_point = BasePoint(
            app.main_frame.control_frame.base_point_frame.entry.ent_1.get(),
            app.main_frame.control_frame.base_point_frame.entry.ent_2.get()
            )
        app_data.base_point = base_point
        app.main_frame.control_frame.refresh_entries()


class EntryFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''Container for entry widgets to hold matrix coefficients.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ent_1 = tk.DoubleVar()
        self.ent_2 = tk.DoubleVar()
        self.col_1 = tk.Entry(self, textvariable=self.ent_1)
        self.col_1.pack(side="left", fill="none", expand=True)
        self.col_2 = tk.Entry(self, textvariable=self.ent_2)
        self.col_2.pack(side="left", fill="none", expand=True)


class SaveFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''A frame to hold widgets related to saving a user-entered matrix in
    the app.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(self, text="Name your matrix",
                              font=("Helvetica", 12))
        self.label.pack(side="top")
        self.container = SimpleFrame(self, side="top", fill="both",
                                     expand=True)
        self.name_label = tk.Label(self.container, text="Name:",
                                   font=("Helvetica", 12))
        self.name_label.pack(side="left")
        self.matrix_name = tk.StringVar()
        self.name_entry = tk.Entry(self.container,
                                   textvariable=self.matrix_name)
        self.name_entry.pack(side="left", fill="none", expand=True)
        self.save_button = tk.Button(self.container, text="Save and refresh",
                                     command=self.save_matrix, height=1,
                                     font=("Helvetica", 8))
        self.save_button.pack(side="left", fill="none", expand=True)

    def save_matrix(self):
        '''Currently just an alias for the update_ap_data() method.'''
        app.main_frame.control_frame.update_app_data()


class PlotFrame(SimpleFrame):  # pylint: disable=too-many-ancestors
    '''Frame to hold a canvas with matplotlib plots.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def replot(self):
        '''Erases old plots and creates a new plot based on the contents
        of app_data.
        '''
        x_1 = app_data.before[0, ]
        y_1 = app_data.before[1, ]
        x_2 = app_data.after[0, ]
        y_2 = app_data.after[1, ]
        entry_list = x_1.tolist() + y_1.tolist() + x_2.tolist() + y_2.tolist()
        max_entry = max(map(abs, entry_list))
        ax_lim = max_entry * 1.2
        self.plot_figure = Figure(figsize=(8, 8), dpi=100)
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.axhline(y=0, color='k')
        self.plot_axis.axvline(x=0, color='k')
        self.plot_axis.grid(True, which='both')
        self.plot_axis.set_axisbelow(True)
        self.plot_axis.plot(x_1, y_1, color='#666666')
        self.plot_axis.plot(x_2, y_2, color='#BB0000')
        self.plot_axis.fill(x_1, y_1, facecolor='#666666', alpha=.5)
        self.plot_axis.fill(x_2, y_2, facecolor='#BB0000', alpha=.5)
        self.plot_axis.set_aspect('equal', 'box')
        self.plot_axis.set_xlim(np.array((-ax_lim, ax_lim)))
        self.plot_axis.set_ylim(np.array((-ax_lim, ax_lim)))
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(self.plot_figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="bottom", fill="both",
                                         expand=True)
        self.canvas._tkcanvas.pack(side="top", fill="both", expand=True)


app = PyMapApp()
app.main_frame.control_frame.refresh_entries()
app.mainloop()
