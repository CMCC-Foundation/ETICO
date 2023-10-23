#!/usr/bin/env python3

# global reqs
from termcolor import colored
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import sys
import pdb
import traceback
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy import interpolate
from configparser import *

# local requirements
from libs.stopping_criteria import *
from libs.config_utilities import *
from libs.matrix_utilities import *
from libs.print_utilities import *
from libs.plot_utilities import *
from libs.exceptions import *

# set the starting point
st_lat = 44.933
st_lon = 12.159


#########################################################
#
# main
#
#########################################################

if __name__ == "__main__":
    
    # Read the name of the NetCDF file
    filename = sys.argv[1]
    configFile = sys.argv[2]
    
    # Open the NetCDF file
    print("[__main__] === Opening file %s" % filename)
    ds = xr.open_dataset(filename)
    
    # Identify the indices of the point that is closest to the given lat and lon
    lat_given = st_lat
    lon_given = st_lon
    lat_idx = abs(ds.lat - lat_given).argmin().values
    lon_idx = abs(ds.lon - lon_given).argmin().values
        
    # Create a list of visited points
    visited = []  
    
    # Initialize a thalweg and a list of the corresponding depths
    thalweg = []
    thalweg_depth = []
    
    # save the original bathy
    ods = ds.copy(deep=True)

    # Start an 'endless' loop
    iterat = 0
        
    #######################################################################
    #
    # READ CONFIG
    #
    #######################################################################
    
    # create a parser and parse the file    
    configDict = read_config(configFile)
    
    #######################################################################
    #
    # MAIN LOOP
    #
    #######################################################################

    while True:
        
        # debug print
        print(colored("__main__", "blue", attrs=["bold"]) + " --- ============================================================")
        print(colored("__main__", "blue", attrs=["bold"]) + " --- Iteration %s with LAT_IDX: %s and LON_IDX: %s with DEPTH %s" % (iterat, lat_idx, lon_idx, ds.bathy.isel(lat=lat_idx, lon=lon_idx).values))

        # get the depth
        depth = get_depth(ds, (lat_idx, lon_idx))
        
        # save the point in thalweg
        thalweg.append((int(lat_idx), int(lon_idx)))
        thalweg_depth.append(depth)
        
        # mark the current cell as visited
        visited.append((int(lat_idx), int(lon_idx)))
        ds.bathy.data[lat_idx, lon_idx] = -np.inf

        # identify the next element based on the zonal direction
        if configDict["maxSearchAlgo"] == "Zonal":
            
            # set the half window size
            halfsize = configDict["windowSize"] // 2
            
            # extract a size x size matrix
            matrix, lat_ind_list, lon_ind_list = get_matrix_centered_on(ds, lat_idx, lon_idx, configDict["windowSize"])
        
            # identify the zonal direction
            zd = get_zonal_direction(matrix, lon_ind_list, lat_ind_list)
            submatrix = get_3x3_submatrix(ds.bathy, lat_idx, lon_idx)
            
            # find the maximum
            next_value, next_coords = find_next_through_zonal_direction(submatrix, zd, lon_idx, lat_idx)
            
        else:
            
            # find the maximum
            next_value, next_coords = find_next_through_classic_direction(ds, lon_idx, lat_idx, configDict["windowSize"])
                        
        # check the identified maximum value
        try:
            next_el_lat_idx = lat_idx + next_coords[0]
            next_el_lon_idx = lon_idx + next_coords[1]
        except TypeError: # our next element is None!
            print(colored("__main__", "blue", attrs=["bold"]) + " --- Our next element is None. END OF THALWEG GENERATION!")
            break                       
        
        next_el_depth = ds.bathy[next_el_lat_idx, next_el_lon_idx].values  
        
        # Update the current point to the one with minimum bathymetry
        lat_idx, lon_idx = next_el_lat_idx, next_el_lon_idx
        depth = get_depth(ds, (lat_idx, lon_idx))
        
        # check neighborhood v2
        neighborhood = get_3x3_submatrix(ds.bathy, lat_idx, lon_idx)
        shouldIstop = checkStop(neighborhood)
        
        # check stopping criteria
        if shouldIstop:
            print(colored("__main__", "blue", attrs=["bold"]) + " --- END OF THALWEG GENERATION!")
            break              
        
        # increment iteration
        iterat += 1
        if iterat == 2000:
            break
        
        # ready for next iteration!
        print(colored("__main__", "blue", attrs=["bold"]) + " --- New matrix will be centered on %s,%s with depth %s" % (lat_idx, lon_idx, depth))

        
    #######################################################################
    #
    # RECAP
    #
    #######################################################################
    
    print(colored("__main__", "blue", attrs=["bold"]) + " ------------------------------------------")
    print(colored("__main__", "blue", attrs=["bold"]) + " --- Our thalweg is:")
    for p in range(len(thalweg)):
        print("%s) - %s [%s]" % (p, thalweg[p], thalweg_depth[p]))


    #######################################################################
    #
    # PLOT
    #
    #######################################################################

    # invoke the plot function
    plot(ods, thalweg, thalweg_depth)

    #######################################################################
    #
    # THE END...
    #
    #######################################################################

    # Close the dataset
    ds.close()  