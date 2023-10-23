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

# local requirements
from libs.matrix_utilities import *
from libs.print_utilities import *


#########################################################
#
# checkStop
#
#########################################################

def checkStop(neighborhood):
    
    """A function to check if stopping criteria are met
    
    Parameters
    ----------
    neighborhood: xarray.core.dataarray.DataArray
        the neighborhood to check
        
    Returns
    -------
    bool
    
    """

    # debug print
    print(colored("libs::stopping_criteria::checkStop", "blue", attrs=["bold"]) + " --- Method starting...")

    # criteria:
    # all the surrounding cells are NaN (out of the river) or -inf (already visited)
        
    # check for criterion 1
    allInfNan = True
    for n in neighborhood:
        if (not np.isinf(n[1])) and (not np.isnan(n[1])):
            allInfNan = False
            break
    cr1 = allInfNan
    
    # return
    return cr1 