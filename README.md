# pymap

This program is a spiritual successor to the map.m program produced by Michael Dellnitz c. 1995, which was in turn adapted from the pplane5.m code by John Polking.  The code will take polygons and matrices from .ini files, load them, and then use matplotlib to show the effect of a selected matrix as a linear transformation on the selected polygon.  Python tkinter and matplotlib are is used to create the GUI, while numpy is used on the back end for calculations.  See pymap.py for formatting information for the .ini files if you want to add new polygons or matrices to the program when it loads.

## Python

Use of this program requires a Python 3 intepreter with the packages numpy, matplotlib, and tkinter installed.  The tkinter package is included in Python distributions by default, but you may need to install the others separately.  If you install the default Python 3.6.6 distribution from [Python.org](https://www.python.org/downloads/), it should come with a package manager called pip, which you can use to install these other packages.

The Anaconda distribution of Python 3.6 from [anaconda.com](https://www.anaconda.com/download/) includes these packages and much more, obviating the need for pip in this instance.

## Using the program

From the dropdown menus, you can select named polygons and matrices to see the effect of a given matrix on a polygon.  If you want to use your own matrix, just enter entries into the "Matrix entries" fields and click the Refresh button.  If you place an unused name in the "Name your matrix" field, the application will add your matrix to the list of matrices for the current session (new matrices will be lost when you close the application, so you should put them in the matrices.ini file if it is important to you that they be around for next time).  You may translate your polygon around the pymap plot, either by changing the values in the "Translate this polygon by" fields or by clicking on the plot.  Resizing the application window should only change the size of the plot, and not the UI.  If you would like to change the appearance of the application, some variables in the PyMapApp class allow for this.
