#!/usr/bin/env python.
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Attempt at duplicating the behavior of Marty's map.m

import Tkinter as tk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class MapPlotApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.title(self, "map")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)

        self.plot_frame = PlotFrame(self, self.container)
        self.plot_frame.pack(side=tk.TOP, fill="both", expand = True)
        
class PlotFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="Here is plot")
        self.label.pack(pady=10,padx=10)             
        
        self.plot_figure = Figure(figsize=(5,5), dpi=100)
        
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.plot(range(0,10), range(0,10))

        self.canvas = FigureCanvasTkAgg(self.plot_figure, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
app = MapPlotApp()
app.mainloop()