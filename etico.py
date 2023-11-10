#!/usr/bin/env python3

# global reqs
from geopy.distance import geodesic
import xarray as xr
import numpy as np
import sys
import csv
import pdb
import os

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
    
    # # find the baseline
    # baseline = find_baseline(ds)

    # # plot the baseline    
    # plot_baseline(baseline, ds, configDict, logFile)

    # check if the start point allows to take a complete matrix,
    # otherwise, create a matrix to fill the gaps
    halfWindowSize = int(configDict["windowSize"]) // 2
    
    # CASE 1: we are too close to bottom margin
    if lat_idx + halfWindowSize > len(ds.lat)-1:
        fullprint("__main__", "Too close to bottom margin", logFile)
        fullprint("__main__", "Setting lat to: %s" % str(len(ds.lat) - 1 - halfWindowSize), logFile)
        
        lat_idx = int(len(ds.lat) - 1 - halfWindowSize)
        lat_given = ds.lat[lat_idx]
        
    # CASE 2: we are too close to top margin
    elif lat_idx - configDict["windowSize"] < 0:
        fullprint("__main__", "Too close to top margin", logFile)
        fullprint("__main__", "Setting lat to: %s" % str(len(ds.lat) - 1 - halfWindowSize), logFile)    
        
        lat_idx = halfWindowSize + 1
        lat_given = ds.lat[lat_idx]

            
    # CASE 3: we are too close to right margin
    if lon_idx + halfWindowSize > len(ds.lat)-1:
        print("TROPPO VICINI AL BORDO DESTRO")
    # CASE 2: we are too close to left margin
    elif lon_idx - configDict["windowSize"] < 0:
        print("TROPPO VICINI AL BORDO SINISTRO")
            

    print("THE NEW STARTING POINT IS:")
    print("%s -- %s -- %s" % (ds.lat[lat_idx].values, ds.lon[lon_idx].values, ds.bathy[lat_idx, lon_idx].values))


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
            
        # find the cells with maximum value
        next_value, shift_coords, d = find_next_through_classic_direction(ds, lon_idx, lat_idx, configDict["windowSize"], directionList, logFile, configDict)
        
        # debug print
        fullprint("__main__", "Next element is %s with direction %s" % (d, next_value), logFile)
    
        # save the last direction
        directionList.append(d)

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
    # PREPARE CSV FILE AND CALCULATE THALWEG LENGTH
    #
    #######################################################################

    # initialize length of the thalweg and prev element
    talLength = 0
    prev = None
    
    # initialise the counter
    counter = 0
    fullprint("__main__", "The log of directions is:", logFile)
    for d in directionList:        
        fullprint("__main__", "%s) - %s [%s] -- DIRECTION %s" % (counter, thalweg[counter], thalweg_depth[counter], d), logFile)
        counter += 1

    # print the thalweg as a sequence of lat,lon couples
    thalwegFilePath = os.path.join(configDict["outputDirectory"], configDict["thalwegFile"])
    thalwegFile = open(thalwegFilePath, "w")
    
    with open(thalwegFilePath, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        for t in thalweg:
            csvwriter.writerow([float(ds.lat[t[0]]), float(ds.lon[t[1]])])

            # for calculating the length, skip if first point
            if  not prev:
                prev = t
                continue
    
            # calculate Euclidean distance
            # d = np.sqrt(np.power(prev[0]-t[0], 2) + np.power(prev[1]-t[1], 2))
            p1 = (float(ds.lat[t[0]]), float(ds.lon[t[1]]))
            p2 = (float(ds.lat[prev[0]]), float(ds.lon[prev[1]]))
            d = geodesic(p1, p2).meters
        
            # update prev and thalweg length
            prev = t
            talLength += d
    
    fullprint("__main__", "Length of the thalweg: %s m" % np.round(talLength, 2), logFile)


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
