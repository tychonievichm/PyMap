#!/usr/bin/env python.
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Attempt at duplicating the behavior of Marty's map.m

import tkinter as tk
from backend import *

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class MapPlotApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.title(self, "PyMap")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.console_frame = tk.Frame(self.container)
        self.main_frame = tk.Frame(self.container)
        self.main_frame.pack(side=tk.LEFT, fill="both", expand = True)

        self.control_frame = ControlFrame(self, self.main_frame)
        self.control_frame.pack(side=tk.LEFT, fill="both", expand = True)
        self.plot_frame = PlotFrame(self, self.main_frame)
        self.plot_frame.pack(side=tk.LEFT, fill="both", expand = True)

class ControlFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.polygon_frame = PolygonFrame(self, parent)
        self.polygon_frame.pack(side="top", fill="both", expand = True)
        self.matrix_frame = MatrixFrame(self, parent)
        self.matrix_frame.pack(side="top", fill="both", expand = True)
        self.base_point_frame = BasePointFrame(self, parent)
        self.base_point_frame.pack(side="top", fill="both", expand = True)

class PolygonFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.choice = tk.StringVar(self)
        self.choices = list(app.plot_frame.ui_data.polygon_dict.keys())
        self.choice.set(self.choices[0])
        self.polygon_menu = tk.OptionMenu(self, self.choice, *self.choices)
        self.polygon_menu.config(width=20, height=1)
        self.polygon_menu.pack(side="top", fill="x", expand=True)
        
        
        

class MatrixFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.options_frame = tk.Frame(self)
        self.options_frame.pack(side="top", fill="x", expand=True)
        self.choice = tk.StringVar(self)
        self.choices = list(app.plot_frame.ui_data.matrix_dict.keys())
        self.choice.set(self.choices[0])
        self.polygon_menu = tk.OptionMenu(self, self.choice, *self.choices)
        self.polygon_menu.config(width=20, height=1)
        self.polygon_menu.pack(side="top", fill="x", expand=True)
        self.row_1_frame = tk.Frame(self)
        self.row_1_frame.pack(side="top", fill="x", expand=True)
        self.entry_11 = tk.Entry(self.row_1_frame)
        self.entry_11.pack(side="left", fill="none", expand=True)
        self.entry_12 = tk.Entry(self.row_1_frame)
        self.entry_12.pack(side="left", fill="none", expand=True)
        self.row_2_frame = tk.Frame(self)
        self.row_2_frame.pack(side="top", fill="x", expand=True)
        self.entry_21 = tk.Entry(self.row_2_frame)
        self.entry_21.pack(side="left", fill="none", expand=True)
        self.entry_22 = tk.Entry(self.row_2_frame)
        self.entry_22.pack(side="left", fill="none", expand=True)
        
class BasePointFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
class PlotFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="Here is plot")
        self.label.pack(pady=10,padx=10)
        
        base_point = Base_Point(1, 2)
        self.ui_data = UI_Data("dogegon", "expanding rotation", base_point)
        
        self.plot_figure = Figure(figsize=(5,5), dpi=100)
        
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.plot(self.ui_data.before[0,], self.ui_data.before[1,], self.ui_data.after[0,], self.ui_data.after[1,])
        self.plot_axis.set_aspect('equal', 'box')
        self.plot_axis.set_xlim(np.array((-3, 3)))
        self.plot_axis.set_ylim(np.array((-3, 3)))
        self.plot_axis.grid(True, which='both')
        self.plot_axis.axhline(y=0, color='k')
        self.plot_axis.axvline(x=0, color='k')
        
        self.canvas = FigureCanvasTkAgg(self.plot_figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
app = MapPlotApp()
app.mainloop()



plt.show()