#!/usr/bin/env python3

# global reqs
import xarray as xr
import numpy as np
import sys

# local requirements
from libs.direction_utilities import *
from libs.stopping_criteria import *
from libs.preproc_utilities import *
from libs.config_utilities import *
from libs.matrix_utilities import *
from libs.print_utilities import *
from libs.plot_utilities import *
from libs.exceptions import *


#########################################################
#
# main
#
#########################################################

if __name__ == "__main__":
    
    #######################################################################
    #
    # PARSE COMMAND LINE
    #
    #######################################################################
    
    # Read the name of the NetCDF file
    try:
        filename = sys.argv[1]
        configFile = sys.argv[2]
    except IndexError:
        fullprint("__main__", "Not enough parameters! Please provide bathymetry file and config file.", error=True)
        sys.exit(100)   
    
    
    #######################################################################
    #
    # READ CONFIG
    #
    #######################################################################
    
    # create a parser and parse the file    
    configDict = read_config(configFile)   
    
    #######################################################################
    #
    # INITIALIZATION
    #
    #######################################################################
    
    # Open the NetCDF file
    fullprint("__main__", "Opening file %s" % filename)
    ds = xr.open_dataset(filename)
    
    # Identify the indices of the point that is closest to the given lat and lon
    lat_given = configDict["startLat"]
    lon_given = configDict["startLon"]
    lat_idx = abs(ds.lat - lat_given).argmin().values
    lon_idx = abs(ds.lon - lon_given).argmin().values

    # Create a list of visited points
    visited = []  
    
    # Initialize a thalweg and a list of the corresponding depths
    thalweg = []
    thalweg_depth = []
    
    # initialize a variable to keep track of the last direction
    lastDirection = None
    directionList = []
    
    # save the original bathy
    ods = ds.copy(deep=True)

    # Start an 'endless' loop
    iterat = 0
    
     
    #######################################################################
    #
    # OPEN LOG FILE
    #
    #######################################################################

    if "logFile" in configDict and "outputDirectory" in configDict:
        logFilePath = os.path.join(configDict["outputDirectory"], configDict["logFile"])
        logFile = open(logFilePath, "w")
    else:
        logFile = None
    
    
    #######################################################################
    #
    # START PREPROC
    #
    #######################################################################
    
    # find the baseline
    baseline = find_baseline(ds)

    # plot the baseline    
    plot_baseline(baseline, ds, configDict, logFile)


    #######################################################################
    #
    # MAIN LOOP
    #
    #######################################################################

    while True:
        
        # debug print 
        fullprint("__main__", "============================================================", logFile)
        fullprint("__main__", "Iteration %s with LAT_IDX: %s and LON_IDX: %s with DEPTH %s" % (iterat, lat_idx, lon_idx, ds.bathy.isel(lat=lat_idx, lon=lon_idx).values), logFile)
        
        # get the depth
        depth = get_depth(ds, (lat_idx, lon_idx))
        
        # save the point in thalweg
        thalweg.append((int(lat_idx), int(lon_idx)))
        thalweg_depth.append(depth)
        fullprint("__main__", " * Adding to the thalweg %s, %s (depth %s)... Let's look at his neighborhood..." % (int(lat_idx), int(lon_idx), depth), logFile)

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
            next_value, shift_coords = find_next_through_zonal_direction(submatrix, zd, lon_idx, lat_idx)
            
        elif configDict["maxSearchAlgo"] == "Classic":
            
            # find the cells with maximum value
            next_value, shift_coords, d = find_next_through_classic_direction(ds, lon_idx, lat_idx, configDict["windowSize"], directionList, logFile)
            
            # debug print
            fullprint("__main__", "Next element is %s with direction %s" % (d, next_value), logFile)

            # save the last direction
            directionList.append(d)
            
        else:
            
            # we should never get here, since we parse the config file
            raise UnsupportedMaxSearchAlgoError()
            sys.exit(27)
                        
        # check the identified maximum value
        try:
            next_el_lat_idx = lat_idx + shift_coords[0]
            next_el_lon_idx = lon_idx + shift_coords[1]
        except TypeError: # our next element is None!
            fullprint("__main__", "Our next element is None. END OF THALWEG GENERATION!", logFile)
            break                       
        
        next_el_depth = ds.bathy[next_el_lat_idx, next_el_lon_idx].values
        
        # Update the current point to the one with minimum bathymetry
        lat_idx, lon_idx = next_el_lat_idx, next_el_lon_idx
        depth = get_depth(ds, (lat_idx, lon_idx))
        
        # check neighborhood v2
        neighborhood = get_3x3_submatrix(ds.bathy, lat_idx, lon_idx)
        print(neighborhood)
        shouldIstop = checkStop(neighborhood)
        
        # check stopping criteria
        if shouldIstop:
            fullprint("__main__", "END OF THALWEG GENERATION!", logFile)
            break              
        
        # increment iteration
        iterat += 1
        if configDict["thalwegStop"] > 0:
            if configDict["thalwegStop"] == iterat:
                break
        
        # ready for next iteration!
        fullprint("__main__", "New matrix will be centered on %s,%s with depth %s" % (lat_idx, lon_idx, depth), logFile)
        if iterat > 10:
            fullprint("__main__", "TREND IS %s --- (%s)" % (get_trend(directionList), directionList[-10:]), logFile)

        
    #######################################################################
    #
    # RECAP
    #
    #######################################################################

    counter = 0
    fullprint("__main__", "The log of directions is:", logFile)
    for d in directionList:        
        fullprint("__main__", "%s) - %s [%s] -- DIRECTION %s" % (counter, thalweg[counter], thalweg_depth[counter], d), logFile)
        counter += 1


    #######################################################################
    #
    # PLOT
    #
    #######################################################################

    # invoke the plot function
    plot(ods, thalweg, thalweg_depth, configDict, logFile)


    #######################################################################
    #
    # THE END...
    #
    #######################################################################

    # Close the dataset
    ds.close()  
    
    # close the log file, if any
    if logFile:
        logFile.close()