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

        # extract a size x size matrix
        size = 9
        halfsize = size // 2
        matrix, lat_ind_list, lon_ind_list = get_matrix_centered_on(ds, lat_idx, lon_idx, size)
        
        # identify the zonal direction
        zd = get_zonal_direction(matrix, lon_ind_list, lat_ind_list)
        submatrix = get_3x3_submatrix(ds.bathy, lat_idx, lon_idx)

        # identify the next element based on the zonal direction
        next_value, next_coords = find_next_through_zonal_direction(submatrix, zd, lon_idx, lat_idx)
        try:
            next_el_lat_idx = lat_idx + next_coords[0]
            next_el_lon_idx = lon_idx + next_coords[1]
        except TypeError: # our next element is None!
            print(colored("__main__", "blue", attrs=["bold"]) + " --- Our next element is a None. END OF THALWEG GENERATION!")
            break                       
        
        next_el_depth = ds.bathy[next_el_lat_idx, next_el_lon_idx].values  
        
        # Update the current point to the one with minimum bathymetry
        lat_idx, lon_idx = next_el_lat_idx, next_el_lon_idx
        depth = get_depth(ds, (lat_idx, lon_idx))
        
        # check neighborhood
        allNanInfVis = True
        neighborhood = get_3x3_submatrix(ds.bathy, lat_idx, lon_idx)
        for n in neighborhood:
            
            # check if nan/inf (inf = already part of the thalweg)
            if (not np.isnan(n[1])) and (not np.isinf(n[1])):
                allNanInfVis = False
                break              
                
        
        # # check neighborhood
        # neighborhood = [((lati, loni), get_depth(ds, (lati, loni))) for lati in lat_ind_list for loni in lon_ind_list ]
        # for n in neighborhood:
        
        #     print("[__main__] === Checking neighbor %s" % str(n))
            
        #     # check if nan/inf (inf = already part of the thalweg)
        #     if (not np.isnan(n[1])) and (not np.isinf(n[1])):
        #         allNanInfVis = False
        #         print("Not all the elements are nan/inf. Found %s" % str(n[1]))
        #         break                
            
        # if all nan/inf (so out of the river or already in the thalweg), the procedure ends
        # otherwise we go on selecting the element with the minimum bathymetry
        if allNanInfVis:
            print(colored("__main__", "blue", attrs=["bold"]) + " --- All the elements are nan/inf. END OF THALWEG GENERATION!")
            break           
        
        # increment iteration
        iterat += 1
        if iterat == 100:
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

    # #######################################################################
    # #
    # # PLOT
    # #
    # #######################################################################

    
    # Close the dataset
    ds.close()  