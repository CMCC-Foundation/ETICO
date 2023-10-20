#!/usr/bin/env python3

# global reqs
from termcolor import colored
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import sys
import pdb
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy import interpolate

# local reqs
from libs.exceptions import *


#########################################################
#
# print_matrix
#
#########################################################

def print_matrix(matrix):
  
    """Just an handler to have a clear/simplified view of a matrix
    
    Parameters
    ----------
    matrix: np.matrix
        a numpy matrix

    Returns
    -------
    bool
        nothing to declare.. :-)
    """

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            strval = str(np.round(matrix[i,j].values, 2)).ljust(4)
            print("%s\t\t" % strval, end='')
        print()
        
    
#########################################################
#
# print_zonal_direction
#
#########################################################

def print_zonal_direction(coords):
  
    """Just an handler to have a symbolic view of the zonal direction
    
    Parameters
    ----------
    coords: list
        a list made by an int for lon shift, one for lat shift

    Returns
    -------
    str
        The symbol for the direction
        
    """

    if (coords[0] == -1) and (coords[1] == -1):
        symb = "\u2196"
    elif (coords[0] == -1) and (coords[1] == 0):
        symb = "\u2191"
    elif (coords[0] == -1) and (coords[1] == 1):
        symb = "\u2197"
    elif (coords[0] == 0) and (coords[1] == -1):
        symb = "\u2190"
    elif (coords[0] == 0) and (coords[1] == 1):
        symb = "\u2192"
    elif (coords[0] == 1) and (coords[1] == -1):
        symb = "\u2199"
    elif (coords[0] == 1) and (coords[1] == 0):
        symb = "\u2193"
    elif (coords[0] == 1) and (coords[1] == 1):
        symb = "\u2198"
    else:
        raise InvalidZonalDirectionError()

    return symb
    