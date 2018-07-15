#!/usr/bin/env python.
# -*- coding: utf-8 -*-
'''
#########################################################################
#                                                                       #
#      Michael Tychonievich, Ph.D.                    July, 2018        #
#             Math Department at The Ohio State University              #
#                                                                       #
#########################################################################

This program is a spiritual successor to the map.m program produced by
Michael Dellnitz c. 1995, which was in turn adapted from the pplane5.m
code by John Polking.  The code will take polygons and matrices from
.ini files, load them, and then use matplotlib to show the effect of
a selected matrix as a linear transformation on the selected polygon.
Python tkinter and matplotlin are is used to create the GUI, while numpy
is used on the back end for calculations.

This program initilizes using two .ini files: polygons.ini and matrices.ini.
If the program does not find either of these files in its working directory,
the missing file will be created with some default values; most of the
defaults were taken directly from Michael Dellnitz's code.

Format for .ini files:
In each file, any blank lines or lines starting with # are ignored when
the file is loaded.  Spaces, colons, line breaks are used for separation,
so care must be taken when writing when adding entries to either file.  All
numerical values will be interpreted as floats.

#########################################################################

Format for polygons.ini to specify a single polygon:

name:<polygon name>
x:<base point x-value> <space-seperated list of x-values>
y:<base point y-value> <space-seperated list of y-values>

<polygon name> will be interpreted as a string and used by the program to
refer to the polygon.  If multiple polygons are given the same name, only the
last one will be included.  Polygons with an empty name will be named.
Any character other than colon and backslash is allowed in this name.

<base point x-value> and <base point y-value> determine what point will
be shifted to the origin by the program when the polygon is loaded.  Users
will effectively be able to determine the position of this point when
manipulating polygons in the program, with the appearance that the polygon
is drawn around it.  This should be some kind of notable reference point for
the polygon, like a corner or barycenter.

<space-seperated list of x-values> and <space-seperated list of y-values>
determine the vertices of the graphed polygon.  The order of these values is
important, as the program will read points off of this list as (x, y) pairs
from left to right when drawing a polygon.  These lists must be of the
same length!  To ensure a closed outline for a polygon, the first and last
point these lists specify should be the same.


Format for matrices.ini to specify a single matrix:

name:<polygon name>
<space-separated list of values>

<matrix name> will be interpreted as a string and used by the program to
refer to the matrix.  If multiple matrices are given the same name, only the
last one will be included.  Matrices with an empty name will be named.
Any character other than colon and backslash is allowed in this name.

<space-separated list of values> are the entries of the 2x2 matrix
                            /a_11 a_12\
                            \a_21 a_22/
given in the order a_11 a_12 a_21 a_22.  There must be exactly four numbers
on this list!

#########################################################################
'''
import os
import sys
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

#########################################################################
#                                                                       #
#                             Backend code                              #
#                                                                       #
#########################################################################


class Polygon:  # pylint: disable=R0903
    '''This object holds the shape to be plotted in the plot window.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        if name is None or name == "":
            name = "MissingNo Error: missing name. "
        if x_list is None and y_list is None:
            x_list = [1, 0]
            y_list = [0, 1]
            name = name + ' Error: missing coordinate values. '
        try:
            self.array = np.array((x_list, y_list), dtype=np.float64)
            self.name = name
        except ValueError:
            self.array = np.array(([0, 0], [0, 0]))
            self.name = name + ' Error coordinate value lists ' +\
                'different lengths or not numeric. '


class Matrix(Polygon):  # pylint: disable=R0903
    '''This object holds the matrix to be used when transforming the shape.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        super().__init__(name, x_list, y_list)
        if self.array.shape != (2, 2):
            self.name = name + ' Error: matrix was not size 2x2. '
            self.array = np.stack(([1, 0], [0, 1]))


class BasePoint(Polygon):  # pylint: disable=R0903
    '''This object holds the base point to be used when translating
    the shape.  The name should never be accessed.
    '''
    def __init__(self, x=0, y=0):
        super().__init__(None, [x], [y])
        if self.array.shape != (2, 1):
            try:
                self.array.shape = (2, 1)
            except ValueError:
                self.array = np.array([0, 0])
                self.name = 'Error: base point did not have two coordinates. '


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
        print('File matrices.ini not found.')
        _renew_matrices_ini()
        matrix_file = open("matrices.ini", "r")
    matrix_data = matrix_file.read()
    matrix_file.close()
    matrix_data = matrix_data.split("\n")
    matrix_data = [data_string for data_string in matrix_data
                   if data_string.strip() != "" and data_string[0] != '#']
    matrix_dict = dict()
    for data_string in matrix_data:
        if data_string.split(":")[0] == "name":
            name = data_string.split(":")[1]
            if name == "":
                name = 'MissingNo Error: this matrix was given an ' +\
                    'incorrectly formatted name. '
            coeff_list = matrix_data[matrix_data.index(
                data_string) + 1].split(" ")
            try:
                coeff_list = [float(entry) for entry in coeff_list]
            except ValueError:
                coeff_list = [1, 0, 0, 1]
                name = name + ' Error: a non-numeric value was given for ' +\
                    'this matrix in matrices.ini. '
            if len(coeff_list) != 4:
                name = name + ' Error: this matrix was given too many ' +\
                    'entries in matrices.ini. '
            matrix_dict[name] = Matrix(name, coeff_list[0:2], coeff_list[2:4])
    return matrix_dict


def _renew_matrices_ini():
    '''Erases matrices.ini and replaces it with the default matrices.ini
    file.
    '''
    print('Creating matrices.ini.')
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
        print('File polygons.ini not found.')
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
            if name == "":
                name = 'MissingNo Error: this matrix was given an ' +\
                    'incorrectly formatted name. '
            coord_list = [0]*2
            try:
                for i in range(2):
                    coord_list[i] = polygon_data[polygon_data.index(
                        data_string) + 1 + i].split(" ")
                    shift = float(coord_list[i].pop(0).split(":")[1])
                    coord_list[i] = [float(entry) - shift for
                                     entry in coord_list[i]]
            except ValueError:
                name = name + ' Error: the numerical data for this ' +\
                    'polygon was incorrectly formatted.'
            polygon_dict[name] = Polygon(name, coord_list[0], coord_list[1])
    return polygon_dict


def _renew_polygons_ini():
    '''Erases polygons.ini and replaces it with the default polygon.ini
    file.
    '''
    print('Creating polygons.ini.')
    polygon_file = open('polygons.ini', 'w+')
    polygons_text = ["name:rectangle\nx:0 0 2 2 0 0\ny:0 0 0 1 1 0\n\n",
                     "name:line\nx:0 0 1.7 0\ny:0 0 0.3 0\n\n",
                     "name:basis\nx:0 0 1 0 0.707 0\ny:0 0 0 0 0.707 0\n\n",
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


app_data = AppData(  # pylint: disable=C0103
    "rectangle", "default", BasePoint(.5, .5)
    )


class SimpleFrame(tk.Frame):  # pylint: disable=R0901
    '''This class is to condense some Frame creation and packing code into
    fewer lines.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, None)
        self.pack(*args, **kwargs)


class BufferFrame:
    """Empty frame for spacing purposes.  This should be a function."""
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
        self.container = SimpleFrame(
            self, side="top", fill="both", expand=True
            )
        self.main_frame = MainFrame(self.container)

    def replot(self):
        '''Currently just an alias.'''
        self.main_frame.plot_frame.replot()


class MainFrame(SimpleFrame):  # pylint: disable=R0901
    '''Temporary class to help organize code.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.control_frame = ControlFrame(
            self, side="left", fill="none", expand=True
            )
        self.plot_frame = PlotFrame(
            self, side="left", fill="both", expand=True
            )


class ControlFrame(SimpleFrame):  # pylint: disable=R0901
    '''Frame to house user controls.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        BufferFrame(self, 40, 1, "top")
        self.polygon_frame = PolygonFrame(
            self, side="top", fill="both", expand=True
            )
        BufferFrame(self, 10, 1, "top")
        self.base_point_frame = BasePointFrame(
            self, side="top", fill="both", expand=True
            )
        BufferFrame(self, 30, 1, "top")
        self.matrix_frame = MatrixFrame(
            self, side="top", fill="both", expand=True
            )
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
        '''This takes the data from the UI and propagates it to app_data.
        Non-numeric entries to numeric field are replaced by default values.
        Attempts at entering complex numbers will be considered non-
        numeric!
        '''
        name = self.matrix_frame.save_frame.matrix_name.get()
        try:
            entry = self.base_point_frame.entry
            base_point = BasePoint(entry.ent_1.get(), entry.ent_2.get())
        except tk.TclError:
            base_point = BasePoint(0, 0)
            name = name + ' Error: a base point entry was non-numeric. '
        app_data.base_point = base_point
        row_1 = self.matrix_frame.row_1
        try:
            x_1 = row_1.ent_1.get()
        except tk.TclError:
            x_1 = 1
            name = name + ' Error: matrix entry (1,1) was non-numeric. '
        try:
            x_2 = row_1.ent_2.get()
        except tk.TclError:
            x_2 = 0
            name = name + ' Error: matrix entry (1,2) was non-numeric. '
        x_list = [x_1, x_2]
        row_2 = self.matrix_frame.row_2
        try:
            y_1 = row_2.ent_1.get()
        except tk.TclError:
            y_1 = 0
            name = name + ' Error: matrix entry (2,1) was non-numeric. '
        try:
            y_2 = row_2.ent_2.get()
        except tk.TclError:
            y_2 = 1
            name = name + ' Error: matrix entry (2,2) was non-numeric. '
        y_list = [y_1, y_2]
        matrix = Matrix(name, x_list, y_list)
        # Save the matrix to the dictionary if an unused name is given, then
        # reload the dropdown menu to allow the matrix to be used again.
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


class PolygonFrame(SimpleFrame):  # pylint: disable=R0901
    '''A frame to hold polygon-related widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(
            self, text="Polygon Name", font=("Helvetica", 12)
            )
        self.label.pack(side="top")
        self.choice = tk.StringVar(self)
        self.choices = list(app_data.polygon_dict.keys())
        self.choice.set(self.choices[0])
        self.menu_frame = MenuFrame(
            self, self.choice, *self.choices, command=self.change_polygon
            )

    @staticmethod
    def change_polygon(choice):
        '''Changes the polygon in app_data when a new selection on the
        pulldown is made.  It then updates the rest of the UI.
        '''
        app_data.polygon = app_data.polygon_dict[choice]
        try:
            entry = app.main_frame.control_frame.base_point_frame.entry
            base_point = BasePoint(entry.ent_1.get(), entry.ent_2.get())
        except tk.TclError:
            base_point = BasePoint(0, 0)
            app_data.polygon.name = app_data.polygon.name +\
                ' Error: base point entry was non-numeric. '
        app_data.base_point = base_point
        app.main_frame.control_frame.refresh_entries()


class MenuFrame(tk.Frame):  # pylint: disable=R0901
    '''Constructs a frame with a dropdown menu and a method to reload it.
    Tkinter does not make it easy to change the options on a dropdown menu,
    so this is my workaround.'''
    def __init__(self, parent, choice, *choices, command=None):
        super().__init__(parent)
        self.pack(side="top", fill="none", expand=True)
        if command is None:
            self.menu = tk.OptionMenu(  # pylint: disable=E1120
                self, choice, *choices
                )
        else:
            self.menu = tk.OptionMenu(  # pylint: disable=E1120
                self, choice, *choices, command=command
                )
        self.menu.config(width=20, height=1)
        self.menu.pack(side="top", fill="x", expand=True)

    def reload(self, choice, *choices, command=None):
        '''Recreates the pulldown menu with an updated options list.  It
        sure would be nice if tkinter.OptionMenus would update dynamically
        with their definig list, but they don't.'''
        try:
            self.menu.destroy()
        except AttributeError:
            pass
        if command is None:
            self.menu = tk.OptionMenu(  # pylint: disable=E1120
                self, choice, *choices
                )
        else:
            self.menu = tk.OptionMenu(  # pylint: disable=E1120
                self, choice, *choices, command=command
                )
        self.menu.config(width=20, height=1)
        self.menu.pack(side="top", fill="x", expand=True)


class BasePointFrame(SimpleFrame):  # pylint: disable=R0901
    '''Temporary class to help organize code.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(
            self, text="Translate the polygon by", font=("Helvetica", 12)
            )
        self.label.pack(side="top")
        self.entry = EntryFrame(self, side="top", fill="x", expand=True)


class MatrixFrame(SimpleFrame):  # pylint: disable=R0901
    '''A frame to hold matrix-related widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(
            self, text="Matrix name", font=("Helvetica", 12)
            )
        self.label.pack(side="top")
        self.choice = tk.StringVar(self)
        self.choices = list(app_data.matrix_dict.keys())
        self.choice.set(self.choices[0])
        self.menu_frame = MenuFrame(
            self, self.choice, *self.choices, command=self.change_matrix
            )
        BufferFrame(self, 10, 1, "top")
        self.label = tk.Label(self, text="Matrix entries",
                              font=("Helvetica", 12))
        self.label.pack(side="top")
        self.row_1 = EntryFrame(self, side="top", fill="x", expand=True)
        self.row_2 = EntryFrame(self, side="top", fill="x", expand=True)
        BufferFrame(self, 10, 1, "top")
        self.save_frame = SaveFrame(
            self, side="top", fill="both", expand=True
            )

    @staticmethod
    def change_matrix(choice):
        '''Changes the matrix in app_data when a new selection on the
        pulldown is made.  It then updates the rest of the UI.
        '''
        app_data.matrix = app_data.matrix_dict[choice]
        try:
            entry = app.main_frame.control_frame.base_point_frame.entry
            base_point = BasePoint(entry.ent_1.get(), entry.ent_2.get())
        except tk.TclError:
            base_point = BasePoint(0, 0)
            app_data.polygon.name = app_data.polygon.name +\
                ' Error: base point entry was non-numeric. '
        app_data.base_point = base_point
        app.main_frame.control_frame.refresh_entries()


class EntryFrame(SimpleFrame):  # pylint: disable=R0901
    '''Container for numeric entry widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ent_1 = tk.DoubleVar()
        self.ent_2 = tk.DoubleVar()
        self.col_1 = tk.Entry(self, textvariable=self.ent_1)
        self.col_1.pack(side="left", fill="none", expand=True)
        self.col_2 = tk.Entry(self, textvariable=self.ent_2)
        self.col_2.pack(side="left", fill="none", expand=True)


class SaveFrame(SimpleFrame):  # pylint: disable=R0901
    '''A frame to hold widgets related to saving a user-entered matrix in
    the app.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(
            self, text="Name your matrix", font=("Helvetica", 12)
            )
        self.label.pack(side="top")
        self.container = SimpleFrame(
            self, side="top", fill="both", expand=True)
        self.name_label = tk.Label(
            self.container, text="Name:", font=("Helvetica", 12)
            )
        self.name_label.pack(side="left")
        self.matrix_name = tk.StringVar()
        self.name_entry = tk.Entry(
            self.container, textvariable=self.matrix_name
            )
        self.name_entry.pack(side="left", fill="none", expand=True)
        self.save_button = tk.Button(
            self.container, text="Save and refresh",
            command=self.save_matrix, height=1, font=("Helvetica", 8)
            )
        self.save_button.pack(side="left", fill="none", expand=True)

    @staticmethod
    def save_matrix():
        '''Currently just an alias for the update_app_data() method.'''
        app.main_frame.control_frame.update_app_data()


class PlotFrame(SimpleFrame):  # pylint: disable=R0901
    '''Frame to hold a canvas with matplotlib plots.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.plot_figure = Figure(figsize=(8, 8), dpi=100)
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.plot_figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(
            side="bottom", fill="both", expand=True
            )
        self.canvas._tkcanvas.pack(  # pylint: disable=W0212
            side="top", fill="both", expand=True
            )

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
        ax_lim = max([max_entry * 1.2, 3])
        self.plot_figure = Figure(figsize=(8, 8), dpi=100)
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.axhline(y=0, color='k')
        self.plot_axis.axvline(x=0, color='k')
        self.plot_axis.grid(True, which='both')
        self.plot_axis.set_axisbelow(True)
        before, = self.plot_axis.plot(x_1, y_1, color='#666666', linewidth=2.5)
        after, = self.plot_axis.plot(x_2, y_2, color='#BB0000', linewidth=2.5)
        self.plot_axis.fill(x_1, y_1, facecolor='#666666', alpha=.5)
        self.plot_axis.fill(x_2, y_2, facecolor='#BB0000', alpha=.5)
        self.plot_axis.set_aspect('equal', 'box')
        self.plot_axis.set_xlim(np.array((-ax_lim, ax_lim)))
        self.plot_axis.set_ylim(np.array((-ax_lim, ax_lim)))
        self.plot_axis.legend(
            [before, after], ['Before Transformation',
                              'After Transformation'], loc='upper right'
            )
        try:
            self.canvas.get_tk_widget().destroy()
        except AttributeError:
            pass
        self.canvas = FigureCanvasTkAgg(self.plot_figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(
            side="bottom", fill="both", expand=True
            )
        self.canvas._tkcanvas.pack(  # pylint: disable=W0212
            side="top", fill="both", expand=True
            )
        self.canvas.mpl_connect('button_press_event', self.onclick)

    @staticmethod
    def onclick(event):
        entry = app.main_frame.control_frame.base_point_frame.entry
        entry.ent_1.set(event.xdata)
        entry.ent_2.set(event.ydata)
        app.main_frame.control_frame.update_app_data()


app = PyMapApp()  # pylint: disable=C0103
app.main_frame.control_frame.refresh_entries()

if hasattr(sys, '_MEIPASS'):
    path = sys._MEIPASS
else:
    path = os.path.abspath(".")
app.iconbitmap(os.path.join(path, 'icon.ico'))
app.mainloop()
