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
from libs.print_utilities import *

    
#########################################################
#
# get_min_through_zonal_direction
#
#########################################################

def get_direction_str(shift_coords):
    
    """Identifies the direction of the next movement
    
    Parameters
    ----------
    shift_coords: list
        A two-elements list with lat shift and lon shift
    
    Returns
    -------
    string
        a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    """
    
    # initialize the direction string
    dirString = ""
    
    # check the lat
    if shift_coords[0] > 0:
        dirString = "S"
    elif shift_coords[0] < 0:
        dirString = "N"
    
    # check the lon
    if shift_coords[1] > 0:
        dirString = "%sE" % dirString
    elif shift_coords[1] < 0:
        dirString = "%sW" % dirString
    
    # return
    return dirString