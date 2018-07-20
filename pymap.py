#!/usr/bin/env python.
# -*- coding: utf-8 -*-
# pylint: disable=E1101,R0901,W0212
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
defaults were taken directly from Michael Dellnitz's code, while everything
else is new.

### Format for .ini files ###

In each file, any blank lines or lines starting with # are ignored when
the file is loaded.  Spaces, colons, line breaks are used for separation,
so care must be taken when writing when adding entries to either file.  All
numerical values will be interpreted as floats.

#########################################################################

# Format for polygons.ini to specify a single polygon #

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


# Format for matrices.ini to specify a single matrix #

name:<polygon name>
<space-separated list of values>

<matrix name> will be interpreted as a string and used by the program to
refer to the matrix.  If multiple matrices are given the same name, only the
last one will be included.  Matrices with an empty name will be named.
Any character other than colon and backslash is allowed in this name.

<space-separated list of values> are the entries of the 2x2 matrix
                            /a[0]1 a[0]2\
                            \a[1]1 a[1]2/
given in the order a[0]1 a[0]2 a[1]1 a[1]2.  There must be exactly four
numberson this list!

#########################################################################
'''
import os
import sys  # os and sys are imported only to look for the program icon
import tkinter as tk  # tkinter powers the GUI

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

#########################################################################
#                                                                       #
#                             Backend code                              #
# This part of the code deals with calculations made before matplotlib  #
# or tkinter are used to create graphics.  It is written so that        #
# upgrading to work with more dimensions will not be too painful,       #
# so that the matplotlib code (and a little bit of the tkinter code)    #
# is the only part that would require significant changes.              #
#                                                                       #
#########################################################################


class Polygon:  # pylint: disable=R0903
    '''This object holds the shape to be plotted in the plot window.
    It's currently set up record any exceptions in the .name property for easy
    display in the GUI for testing while the console is not visible (and
    because bad user inputs are almost certainly how these issues arise in
    the first place.).  Polygon and its subclasses are essentially numpy
    arrays with some special initialization requirements, but I found it
    convenient to have a special "array" field.
    '''
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
    '''This object holds the matrix to be used when transforming the shape.
    Both are numpy arrays with the same number of rows, but a matrix must have
    two columns.
    '''
    def __init__(self, name=None, x_list=None, y_list=None):
        super().__init__(name, x_list, y_list)
        if self.array.shape != (2, 2):
            self.name = name + ' Error: matrix was not size 2x2. '
            self.array = np.array(([1, 0], [0, 1]))


class BasePoint(Polygon):  # pylint: disable=R0903
    '''This object holds the base point to be used when translating
    the shape.  The name should never be accessed outside of debugging, but
    it might be useful to add a list of predefined base point values to the
    program so I left it on.
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

    def add_matrix_to_dict(self, matrix):
        '''Add a matrix to the matrix dictionary.'''
        self.matrix_dict[matrix.name] = matrix

    def add_polygon_to_dict(self, polygon):
        '''Add a polygon to the polygon dictionary.'''
        self.polygon_dict[polygon.name] = polygon


def _read_matrices_to_dict():
    '''Get the list of matrices from the matrices.ini file.'''
    try:
        matrix_file = open("matrices.ini", "r")
    except FileNotFoundError:
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
    '''Erase matrices.ini and replace it with the default matrices.ini
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
    '''Get the list of polygons from the polygons.ini file.'''
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
    '''Erase polygons.ini and replace it with the default polygon.ini
    file.
    '''
    print('Creating polygons.ini.')
    polygon_file = open('polygons.ini', 'w+')
    polygons_text = ["name:rectangle\nx:0 0 1 1 0 0\ny:0 0 0 0.5 0.5 0\n\n",
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


class SimpleFrame(tk.Frame):
    '''Convenience class to condense some Frame creation and packing code into
    fewer lines.  The root field is there to remember what tkinter app the
    frame belongs too.
    '''
    def __init__(self, parent, *args, root=None, **kwargs):
        super().__init__(parent, None)
        self.root = root
        self.pack(*args, **kwargs)


def spacer(parent, ht, wd, sd):
    """Empty frame for spacing purposes."""
    container = tk.Frame(parent, height=ht, width=wd)
    container.pack(side=sd, expand=False)
    return container


class PyMapApp(tk.Tk):
    '''This is the main tkinter application.  It creates several frames
    using the data from app_data, with the data moved to the UI after
    the tkinter app has completely loaded.  Several of the classes
    could be replaced by functions, but they were left in because it
    makes it simpler to add features in the future.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().title("pymap")
        self.data = AppData(
                    "rectangle", "default", BasePoint(.5, .5)
                    )
        self.container = SimpleFrame(
            self, side="top", fill="both", expand=True, root=self
            )
        self.control_adjuster = SimpleFrame(
            self.container, side="left", fill="y", expand=False
            )
        self.control_adjuster.root = self
        self.control_frame = ControlFrame(
            self.control_adjuster, side="top", fill="none", expand=False
            )
        self.plot_frame = PlotFrame(
            self.container, side="left", fill="both", expand=True
            )


class ControlFrame(SimpleFrame):
    '''Frame to house user controls.  Its methods govern the tkinter app
    behavior.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent.root
        spacer(self, 40, 1, "top")
        self.polygon_frame = PolygonFrame(
            self, side="top", fill="both", expand=True
            )
        spacer(self, 10, 1, "top")
        self.base_point_frame = BasePointFrame(
            self, side="top", fill="both", expand=True
            )
        spacer(self, 30, 1, "top")
        self.matrix_frame = MatrixFrame(
            self, side="top", fill="both", expand=True
            )
        spacer(self, 40, 1, "top")

    def refresh_entries(self):
        '''This takes the data from root.data and propagates it to the UI.
        before refreshing the plot figure.
        '''
        base_point = self.root.data.base_point.array
        base_entry = self.base_point_frame.entry
        array = self.root.data.matrix.array
        row = self.matrix_frame.row
        name = self.root.data.matrix.name
        self.matrix_frame.save_frame.matrix_name.set(name)
        for row_index in range(2):
            base_entry.ent[row_index].set(float(base_point.item(row_index, 0)))
            for col_index in range(2):
                row[row_index].ent[col_index].set(
                    array.item(row_index, col_index)
                    )
        self.root.data.make_plot_polygon()
        self.root.data.make_transformed_polygon()
        self.root.plot_frame.replot()

    def update_app_data(self):
        '''This takes the data from the UI and propagates it to root.data.
        Non-numeric entries to numeric field are replaced by default values.
        Attempts at entering complex numbers will be considered non-
        numeric!  This should be rewritten so that the numbers are put in a
        single list instead of two.
        '''
        name = self.matrix_frame.save_frame.matrix_name.get()
        row = self.matrix_frame.row
        x_list = [""] * 2
        y_list = [""] * 2
        try:
            entry = self.base_point_frame.entry
            base_point = BasePoint(entry.ent[0].get(), entry.ent[1].get())
        except tk.TclError:
            base_point = BasePoint(0, 0)
            name = name + ' Error: a base point entry was non-numeric. '
        self.root.data.base_point = base_point
        for row_index in range(2):
            try:
                x_list[row_index] = row[0].ent[row_index].get()
            except tk.TclError:
                x_list[row_index] = 0
                name = name + ' Error: a matrix entry was non-numeric. '
            try:
                y_list[row_index] = row[1].ent[row_index].get()
            except tk.TclError:
                y_list[row_index] = 1
                name = name + ' Error: a matrix entry was non-numeric. '
        matrix = Matrix(name, x_list, y_list)
        # Save the matrix to the dictionary if an unused name is given, then
        # reload the dropdown menu to allow the matrix to be used again.
        if name not in list(self.root.data.matrix_dict.keys()):
            self.root.data.add_matrix_to_dict(matrix)
            self.matrix_frame.choices.append(name)
            self.matrix_frame.choice.set(name)
            self.matrix_frame.menu_frame.reload(
                self.matrix_frame.choice,
                *self.matrix_frame.choices,
                command=self.matrix_frame.change_matrix
                )
        self.root.data.matrix = matrix
        self.refresh_entries()

    def change_polygon(self, choice):
        '''Changes the polygon in root.data when a new selection on the
        pulldown is made.  It then updates the rest of the UI.
        '''
        self.root.data.polygon = self.root.data.polygon_dict[choice]
        try:
            entry = self.base_point_frame.entry
            base_point = BasePoint(entry.ent[0].get(), entry.ent[1].get())
        except tk.TclError:
            base_point = BasePoint(0, 0)
            self.root.data.polygon.name = self.root.data.polygon.name +\
                ' Error: base point entry was non-numeric. '
        self.root.data.base_point = base_point
        self.refresh_entries()

    def change_matrix(self, choice):
        '''Changes the matrix in root.data when a new selection on the
        pulldown is made.  It then updates the rest of the UI.
        '''
        self.root.data.matrix = self.root.data.matrix_dict[choice]
        try:
            entry = self.base_point_frame.entry
            base_point = BasePoint(entry.ent[0].get(), entry.ent[1].get())
        except tk.TclError:
            base_point = BasePoint(0, 0)
            self.root.data.polygon.name = self.root.data.polygon.name +\
                ' Error: base point entry was non-numeric. '
        self.root.data.base_point = base_point
        self.refresh_entries()


class PolygonFrame(SimpleFrame):
    '''A frame to hold polygon-related widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent.root
        self.label = tk.Label(
            self, text="Polygon", font=("Helvetica", 12)
            )
        self.label.pack(side="top")
        self.choice = tk.StringVar(self)
        self.choices = list(self.root.data.polygon_dict.keys())
        self.choice.set(self.choices[0])
        self.menu_frame = MenuFrame(
            self, self.choice, *self.choices, command=self.change_polygon
            )

    def change_polygon(self, choice):
        '''Currently just an alias for the change_polygon() method.'''
        self.root.control_frame.change_polygon(choice)


class MenuFrame(tk.Frame):
    '''Constructs a frame with a dropdown menu and a method to reload it.
    Tkinter does not make it easy to change the options on a dropdown menu,
    so this is my workaround.'''
    def __init__(self, parent, choice, *choices, command=None):
        super().__init__(parent)
        self.pack(side="top", fill="none", expand=True)
        self.menu = tk.OptionMenu(  # pylint: disable=E1120
                self, choice, *choices
                )
        self.reload(choice, *choices, command=command)

    def reload(self, choice, *choices, command=None):
        '''Recreates the pulldown menu with an updated options list.  It
        sure would be nice if a tkinter.OptionMenu would update dynamically
        with its defining list, but it doesn't.'''
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
        self.menu.config(width=13, height=1, font=("Helvetica", 8))
        self.menu.pack(side="top", fill="x", expand=True)


class BasePointFrame(SimpleFrame):
    '''Temporary class to help organize code.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(
            self, text="Translate the polygon by", font=("Helvetica", 10)
            )
        self.label.pack(side="top")
        self.entry = EntryFrame(self, side="top", fill="x", expand=True)


class MatrixFrame(SimpleFrame):
    '''A frame to hold matrix-related widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent.root
        self.label = tk.Label(
            self, text="Matrix", font=("Helvetica", 12)
            )
        self.label.pack(side="top")
        self.choice = tk.StringVar(self)
        self.choices = list(self.root.data.matrix_dict.keys())
        self.choice.set(self.choices[0])
        self.menu_frame = MenuFrame(
            self, self.choice, *self.choices, command=self.change_matrix
            )
        spacer(self, 10, 1, "top")
        self.label = tk.Label(self, text="Matrix entries",
                              font=("Helvetica", 10))
        self.label.pack(side="top")
        self.row = [""] * 2
        self.row[0] = EntryFrame(self, side="top", fill="x", expand=True)
        self.row[1] = EntryFrame(self, side="top", fill="x", expand=True)
        spacer(self, 10, 1, "top")
        self.save_frame = SaveFrame(
            self, side="top", fill="both", expand=True
            )

    def change_matrix(self, choice):
        '''Currently just an alias for the change_matrix() method.'''
        self.root.control_frame.change_matrix(choice)


class EntryFrame(SimpleFrame):
    '''Container for numeric entry widgets.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ent = [""] * 2
        self.col = [""] * 2
        for index in range(2):
            self.ent[index] = tk.DoubleVar()
            self.col[index] = tk.Entry(
                self, textvariable=self.ent[index], width=10
                )
            self.col[index].pack(side="left", fill="none", expand=True)


class SaveFrame(SimpleFrame):
    '''A frame to hold widgets related to saving a user-entered matrix in
    the app.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent.root
        self.label = tk.Label(
            self, text="Name your matrix", font=("Helvetica", 10)
            )
        self.label.pack(side="top")
        self.container = SimpleFrame(
            self, side="top", fill="both", expand=True)
        '''self.name_label = tk.Label(
            self.container, text="Name:", font=("Helvetica", 10)
            )
        self.name_label.pack(side="left")'''
        self.matrix_name = tk.StringVar()
        self.name_entry = tk.Entry(
            self.container, textvariable=self.matrix_name, width=13,
            font=("Helvetica", 8)
            )
        self.name_entry.pack(side="left", fill="none", expand=True)
        self.save_button = tk.Button(
            self.container, text="Refresh",
            command=self.save_matrix, height=1, font=("Helvetica", 8)
            )
        self.save_button.pack(side="left", fill="none", expand=True)

    def save_matrix(self):
        '''Currently just an alias for the update_app_data() method.'''
        self.root.control_frame.update_app_data()


class PlotFrame(SimpleFrame):
    '''Frame to hold a canvas with matplotlib plots.'''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent.root
        self.plot_figure = Figure(figsize=(5, 5), dpi=100)
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.set_axisbelow(True)
        self.plot_axis.set_aspect('equal', 'box')
        self.plot_before = None
        self.plot_after = None
        self.fill_before = None
        self.fill_after = None
        self.canvas = FigureCanvasTkAgg(self.plot_figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(
            side="top", fill="both", expand=True,
            )
        self.canvas.mpl_connect('button_press_event', self.onclick)

    def replot(self):
        '''Erases old plots and creates a new plot based on the contents
        of root.data.
        '''
        x = 2*[""]  # pylint: disable=C0103
        y = 2*[""]  # pylint: disable=C0103
        x[0] = self.root.data.before[0, ]
        y[0] = self.root.data.before[1, ]
        x[1] = self.root.data.after[0, ]
        y[1] = self.root.data.after[1, ]
        ax_lim = 4.5
        '''  # Automatic axis rescaling.
        entry_list = x[0].tolist() + y[0].tolist() + x[1].tolist() +\
            y[1].tolist()
        max_entry = max(map(abs, entry_list))
        ax_lim = max([max_entry * 1.2, 3])
        '''
        self.plot_axis.clear()
        self.plot_axis.axhline(y=0, color='k')
        self.plot_axis.axvline(x=0, color='k')
        self.plot_axis.grid(True, which='both')
        self.plot_before = self.plot_axis.plot(
            x[0], y[0], color='#666666', linewidth=2.5
            )
        self.plot_after = self.plot_axis.plot(
            x[1], y[1], color='#BB0000', linewidth=2.5
            )
        self.fill_before = self.plot_axis.fill(
            x[0], y[0], facecolor='#666666', alpha=.5
            )
        self.fill_after = self.plot_axis.fill(
            x[1], y[1], facecolor='#BB0000', alpha=.5
            )
        before, = self.plot_before
        after, = self.plot_after
        self.plot_axis.legend(
            [before, after], ['Before',
                              'After'], loc='upper right',
            fontsize=8, fancybox=True
            )
        self.plot_axis.set_xlim(np.array((-ax_lim, ax_lim)))
        self.plot_axis.set_ylim(np.array((-ax_lim, ax_lim)))
        self.plot_axis.set_title(
            "pymap plot by matplotlib.pyplot", fontsize=10, loc='right'
            )
        self.canvas.draw()

    def onclick(self, event):
        '''Places coordinate information in the UI when the user clicks on
        the plot and then updates the app using the coordinates as a base
        point for the polygon.'''
        entry = app.control_frame.base_point_frame.entry
        if event.xdata is not None and event.ydata is not None:
            entry.ent[0].set(event.xdata)
            entry.ent[1].set(event.ydata)
            self.root.control_frame.update_app_data()


app = PyMapApp()  # pylint: disable=C0103
app.control_frame.refresh_entries()
# This detects if the program is running from a file instead of an
# interpreter and loads the app icon appropriately.
try:
    if hasattr(sys, '_MEIPASS'):
        path = sys._MEIPASS  # pylint: disable=C0103
    else:
        path = os.path.abspath(".")  # pylint: disable=C0103
        app.iconbitmap(os.path.join(path, 'icon.ico'))
finally:
    app.mainloop()
