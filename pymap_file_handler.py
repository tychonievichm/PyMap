#!/usr/bin/env python.
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #

import numpy as np
import matplotlib.pyplot as plt


class Shape:
    '''This object holds the shape to be plotted in the plot window.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        self.array = np.stack((x_list, y_list))
        self.name = name

class Matrix(Shape):
    '''This object holds the matrix to be used when transforming the shape.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        super().__init__(name, x_list, y_list)
        
class Base_Point:
    def __init__(self, x=0, y=0):
        self.array = np.array((x, y))
        self.array.shape = (2,1)
        
    
class UI_Data:
    def __init__(self, shape=None, matrix=None, base_point=None):
        self.shape = shape
        self.matrix = matrix
        self.base_point = base_point
        self.make_plot_shape()
        self.make_transform_shape()
        
    def make_plot_shape(self):
        self.before = self.shape.array + self.base_point.array
    
    def make_transform_shape(self):
        self.after = self.matrix.array @ self.before

def _read_code_to_dict(file_name):
    """Convert a text file into a dictionary of CodeLines."""
    f = open(file_name, "r")
    turing_code = f.read()
    # If IOError is raised here, the program quits.
    f.close()
    turing_code = turing_code.split("\n")
    turing_code = {s for s in turing_code if s.strip() != "" and s[0] != '#'}
    # Remove comments and blank lines.
    code_dict = {_CodeLine(s).key: _CodeLine(s) for s in turing_code}
    if " " in code_dict.keys():
        code_dict.pop(" ")
    return code_dict












shape = Shape('testshape',[1, 2, 3, 4, 5],[3, 7, 5, 4, 7])
matrix = Matrix('testmat', [0, 1], [1, 0])
base_point = Base_Point(1, 2)
ui = UI_Data(shape, matrix, base_point)
plt.plot(ui.before[0,], ui.before[1,])
plt.plot(ui.after[0,], ui.after[1,])