#!/usr/bin/env python.
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #

import numpy as np
import matplotlib.pyplot as plt


class Polygon:
    '''This object holds the shape to be plotted in the plot window.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        self.array = np.stack((x_list, y_list))
        self.name = name

class Matrix(Polygon):
    '''This object holds the matrix to be used when transforming the shape.'''
    def __init__(self, name=None, x_list=None, y_list=None):
        super().__init__(name, x_list, y_list)
        
class Base_Point:
    def __init__(self, x=0, y=0):
        self.array = np.array((x, y))
        self.array.shape = (2,1)

class UI_Data:
    def __init__(self, polygon_name=None, matrix_name=None, base_point=None):
        self.polygon_dict = _read_polygons_to_dict()
        self.matrix_dict = _read_matrices_to_dict()
        self.polygon = self.polygon_dict[polygon_name]
        self.matrix = self.matrix_dict[matrix_name]
        self.base_point = base_point
        self.make_plot_polygon()
        self.make_transformed_polygon()
        
    def make_plot_polygon(self):
        self.before = self.polygon.array + self.base_point.array
    
    def make_transformed_polygon(self):
        self.after = self.matrix.array @ self.before

def _read_matrices_to_dict():
    f = open("matrices.ini", "r")
    matrix_data = f.read()
    f.close()
    matrix_data = matrix_data.split("\n")
    matrix_data = [s for s in matrix_data if s.strip() != "" and s[0] != '#']
    matrix_dict = dict()
    for s in matrix_data:
        if s.split(":")[0] == "name":
            name = s.split(":")[1]
            coeff_list = (matrix_data[matrix_data.index(s) + 1]).split(" ")
            coeff_list = [float(t) for t in coeff_list]
            matrix_dict[name] = Matrix(name, coeff_list[0:2], coeff_list[2:])
            # print("Added matrix " + name)
    return matrix_dict

def _read_polygons_to_dict():
    f = open("polygons.ini", "r")
    polygon_data = f.read()
    f.close()
    polygon_data = polygon_data.split("\n")
    polygon_data = [s for s in polygon_data if s.strip() != "" and s[0] != '#']
    polygon_dict = dict()
    for s in polygon_data:
        if s.split(":")[0] == "name":
            name = s.split(":")[1]
            coord_list = [0]*2
            for i in range(2):
                coord_list[i] = polygon_data[polygon_data.index(s) + 1 + i].split(" ")
                shift = float(coord_list[i].pop(0).split(":")[1])
                coord_list[i] = [float(t) - shift for t in coord_list[i]]
            polygon_dict[name] = Polygon(name, coord_list[0], coord_list[1])
    return polygon_dict

base_point = Base_Point(1, 2)
ui = UI_Data("dogegon", "default", base_point)
ax = plt.subplot(111)
plt.plot(ui.before[0,], ui.before[1,], ui.after[0,], ui.after[1,])

ax.set_aspect('equal', 'box')
ax.set_xlim(np.array((-3, 3)))
ax.set_ylim(np.array((-3, 3)))
ax.grid(True, which='both')
ax.axhline(y=0, color='k')
ax.axvline(x=0, color='k')
plt.show()
