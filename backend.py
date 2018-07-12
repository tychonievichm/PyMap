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
    '''Gets the list of matrices from the matrices.ini file.'''
    try:
        f = open("matrices.ini", "r")
    except FileNotFoundError:
        _renew_matrices_ini()
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

def _renew_matrices_ini():
    '''Erases matrices.ini and replaces it with the default matrices.ini file.'''
    f = open('matrices.ini', 'w+')
    matrices_text = ["name:default\n0 1 -1 0\n\n",
                     "name:contracting rotation\n0.3 0.8 -0.8 0.3\n\n",
                     "name:expanding rotation\n0.9 0.7 -0.7 0.9\n\n",
                     "name:real eigenvalues\n0.2 -1.8 -1.2 0.8\n"]
    for s in matrices_text:
        f.write(s)
    f.close

def _read_polygons_to_dict():
    '''Gets the list of polygons from the polygons.ini file.'''
    try:
        f = open("polygons.ini", "r")
    except FileNotFoundError:
        _renew_polygons_ini()
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


                    
def _renew_polygons_ini():
    '''Erases polygons.ini and replaces it with the default polygon.ini file.'''
    f = open('polygons.ini', 'w+')
    polygons_text = ["name:rectangle\nx:0 0 2 2 0 0\ny:0 0 0 1 1 0\n\n",
                     "name:line\nx:0 0 1.7 0\ny:0 0 0.3 0\n\n",
                     "name:basis\nx:0 0 0 0 1 0\ny:0 0 1 0 0 0\n\n",
                     "name:square\nx:0 0 1 1 0 0\ny:0 0 0 1 1 0\n\n",
                     "name:dogegon\nx:1.3850 0.8711 1.0166 1.1751 1.7441 ",
                     "2.0674 1.9413 1.8443 1.7861 1.7279 1.2818 1.1977 1.1686 ",
                     "1.0490 1.0360 0.8679 0.8711\ny:1.4246 1.6176 1.8261 ",
                     "1.6097 1.5595 1.4302 1.3378 1.3378 1.0422 1.3326 1.3378 ",
                     "1.0106 1.3194 1.4012 1.5886 1.6176 1.6176\n\n"]
    for s in polygons_text:
        f.write(s)
    f.close

base_point = Base_Point(1, 2)
ui = UI_Data("dogegon", "expanding rotation", base_point)
ax = plt.subplot(111)
plt.plot(ui.before[0,], ui.before[1,], ui.after[0,], ui.after[1,])

ax.set_aspect('equal', 'box')
ax.set_xlim(np.array((-3, 3)))
ax.set_ylim(np.array((-3, 3)))
ax.grid(True, which='both')
ax.axhline(y=0, color='k')
ax.axvline(x=0, color='k')
plt.show()
