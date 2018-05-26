#!/usr/bin/env python.
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Attempt at duplicating the behavior of Marty's map.m

import Tkinter as tk

import matplotlib
import numpy as np


# plotting code goes here.  todo: plot a filled shape that was
# placed on a figure by the user with a mouse click (or maybe 
# a drag?) and then the transformed version of it.  User should
# have a UI to enter the matrix used, and a small gallery of 
# "default" matrices.  Need to have a UI to choose fill color
# and outline color.  the clicky stuff will be done in the other
# program, but the plotty stuff should be done here