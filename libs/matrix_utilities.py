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
from libs.direction_utilities import *

    
#########################################################
#
# get_min_through_zonal_direction
#
#########################################################

def get_zonal_direction(matrix, lats, lons, logFile=None):
    
    """Identifies the next element through the zonal direction

    Parameters
    ----------
    matrix: np.matrix
        The 9x9 submatrix extracted from the global one
    lats: list
        An array of the latitudes included in the submatrix
    lons: list
        An array of the longitudes included in the submatrix
    logFile: fileDescriptor
        A file descriptor for logging

    Returns
    -------
    list
        a list containing the shift on lon and lat for the zonal direction:
        -1,-1 (NW)   -1,0 (N)   -1,1 (NE)
         0,-1 (W)                0,1 (E)
         1,-1 (SW)    1,0 (S)    1,1 (SE)
    """
    
    # 0 - initialize data structures
    matrices = {}
    matrices_max_values = []
    final_matrix = np.full((3, 3), np.nan)
    
    # take as input the 9x9 matrix and split it into n/3 3x3 matrices
    # this step is the "maximum resampling"
    lon_counter = 0
    for i in range(lons[0]+1, lons[-1], 3):

        lat_counter = 0
        for j in range(lats[0]+1, lats[-1], 3):
            
            if (lat_counter == 1) and (lon_counter == 1):
                final_matrix[lon_counter, lat_counter] = -np.inf
                lat_counter += 1
                continue
            
            # get local index
            local_i = lons.index(i)
            local_j = lats.index(j)
            
            # extract submatrix
            submatrix = get_3x3_submatrix(matrix, local_i, local_j)
            matrices["matrix"] = submatrix
    
            # identify the maximum (i.e. the deepest point)
            coords, value = find_max(submatrix)
            matrices["min_local_coords"] = coords
            matrices["min_local_value"] = value
                        
            # start filling the final matrix
            final_matrix[lon_counter, lat_counter] = value 
            
            # increment the lon counter
            lat_counter += 1
        
        # increment the lat counter
        lon_counter += 1
    
    # identify them minimum in this matrix, then the zonal direction
    fullprint("get_zonal_direction", "Resampled matrix is:", logFile)
    fullprint_matrix(final_matrix)
    
    coords,value = find_max(final_matrix)
    zd = [coords[0]-1, coords[1]-1]
    fullprint("get_zonal_direction", "Zonal direction is %s,%s %s" % (zd[0], zd[1], print_zonal_direction(zd)), logFile)


    # return
    return zd

#########################################################
#
# find_max
#
#########################################################

def find_max(matrix):
 
    """Identifies the next element through the zonal direction

    Parameters
    ----------
    matrix: np.matrix
        The 9x9 submatrix extracted from the global one
    lats: list
        An array of the latitudes included in the submatrix
    lons: list
        An array of the longitudes included in the submatrix

    Returns
    -------
    list
        a list containing the lat and lon of the next element
    """

    # 0 - identify the maximum value in the matrix
    try:
        coords = np.unravel_index(np.nanargmax(matrix), matrix.shape)
        value = float(matrix[coords])
    except ValueError:
        return (None, None), np.nan

    # return the coordinates and the value
    return coords, value

    
#########################################################
#
# get_3x3_centered_on function
#
#########################################################

def get_3x3_submatrix(ds, lat_idx, lon_idx):
 
    """Extract a 3x3 submatrix, given its center

    Parameters
    ----------
    matrix: np.matrix
        The original data from which to extract the submatrix
    lat_idx: int
        The latitude index of the center
    lon_idx: int
        The longitude index of the center

    Returns
    -------
    np.matrix
        a 3x3 submatrix centered in lat_idx, lon_idx
    """
    
    # extract and return submatrix
    return ds.isel(lat=slice(lat_idx-1, lat_idx+2), lon=slice(lon_idx-1, lon_idx+2))
    

#########################################################
#
# find_max_through_zonal_direction
#
#########################################################

def find_next_through_zonal_direction(matrix, coords, lon_idx, lat_idx, logFile=None):
    
    """Extract the max from the 3 elements of the matrix identified by zonal direction

    Parameters
    ----------
    matrix: np.matrix
        The 3x3 matrix where to look for the maximum
    coords: list
        The lat and lon indices identifying the zonal direction
    logFile: fileDescriptor
        A file descriptor for logging purposes

    Returns
    -------
    np.matrix
        a 3x3 submatrix centered in lat_idx, lon_idx
    """

    # initialize the three elements structure
    sel_three = []
    
    print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Submatrix where to look for the maximum:")
    print_matrix(matrix)
    
    # first row ( NW -- N -- NE )
    
    if (coords[0] == -1) and (coords[1] == -1): # NW
    
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going NorthWest")
        sel_three.append({"value": float(matrix[0, 0].values),   "coords": [-1, -1]})
        sel_three.append({"value": float(matrix[0, 1].values),   "coords": [-1, 0]})
        sel_three.append({"value": float(matrix[1, 0].values),   "coords": [0, -1]})

    elif (coords[0] == -1) and (coords[1] == 0): # N
    
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going North")
        sel_three.append({"value": float(matrix[0, 0].values),   "coords": [-1, -1]})
        sel_three.append({"value": float(matrix[0, 1].values),   "coords": [-1, 0]})
        sel_three.append({"value": float(matrix[0, 2].values),   "coords": [-1, 1]})

    elif (coords[0] == -1) and (coords[1] == 1): # NE

        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going NorthEast")
        sel_three.append({"value": float(matrix[0, 1].values),   "coords": [-1, 0]})
        sel_three.append({"value": float(matrix[0, 2].values),   "coords": [-1, 1]})
        sel_three.append({"value": float(matrix[1, 2].values),   "coords": [0, 1]})

    # second row ( W -- E )

    elif (coords[0] == 0) and (coords[1] == -1): # W
    
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going West")
        sel_three.append({"value": float(matrix[0, 0].values),   "coords": [-1, -1]})
        sel_three.append({"value": float(matrix[1, 0].values),   "coords": [0, -1]})
        sel_three.append({"value": float(matrix[2, 0].values),   "coords": [1, -1]})

    elif (coords[0] == 0) and (coords[1] == 1): # E
    
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going East")
        sel_three.append({"value": float(matrix[0, 2].values),   "coords": [-1, 1]})
        sel_three.append({"value": float(matrix[1, 2].values),   "coords": [0, 1]})
        sel_three.append({"value": float(matrix[2, 2].values),   "coords": [1, 1]})

    # third row ( SW -- S -- SE )

    elif (coords[0] == 1) and (coords[1] == 1): # SE
    
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going SouthEast")
        sel_three.append({"value": float(matrix[2, 1].values),   "coords": [1, 0]})
        sel_three.append({"value": float(matrix[2, 2].values),   "coords": [1, 1]})
        sel_three.append({"value": float(matrix[1, 2].values),   "coords": [0, 1]})

    elif (coords[0] == 1) and (coords[1] == 0): # S [1,0]
 
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going South")
        sel_three.append({"value": float(matrix[2, 0].values),   "coords": [1, -1]})
        sel_three.append({"value": float(matrix[2, 1].values),   "coords": [1, 0]})
        sel_three.append({"value": float(matrix[2, 2].values),   "coords": [1, 1]})

    elif (coords[0] == 1) and (coords[1] == -1): # SW [1,-1]
    
        print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Going SouthWest")
        sel_three.append({"value": float(matrix[1, 2].values),   "coords": [0, 1]})
        sel_three.append({"value": float(matrix[2, 2].values),   "coords": [1, 1]})
        sel_three.append({"value": float(matrix[2, 1].values),   "coords": [1, 0]})

    # other values

    else:   
        raise InvalidZonalDirectionError()

    # determine and return the maximum elements and its coordinates
    max_value = -np.inf
    max_coords = None
    for el in sel_three:
        print(el)
        if el["value"] > max_value:
            max_value = el["value"]
            max_coords = el["coords"]
            
    # if coords are None, then extend the research to the whole submatrix
    if max_coords == None:
        max_coords, max_value = find_max(matrix)
        if np.isinf(max_value):
            return None, None
        else:
            max_coords = [max_coords[0]-1, max_coords[1]-1]
            
    print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Returning %s, %s" % (max_value, max_coords))
    return max_value, max_coords
            
    
#########################################################
#
# find_next_through_classic_direction function
#
#########################################################

def find_next_through_classic_direction(ds, lon_idx, lat_idx, window_size, directionList, logFile):
     
    """Extract the next element through the classic method
    
    Parameters
    ----------
    ds: np.matrix
        The n x n matrix where to look for the next element
    lat_idx: int
        Latitude index of the center of the matrix
    lon_idx: list
        Longitude index of the center of the matrix
    window_size: int
        The size of the window
    directionList: list
        The list of the all the directions took in the past
    logFile: fileDescriptor
        A file descriptor for logging purposes

    Returns
    -------
    list
        a list containing the lat and lon of the next element
    """  
    
    # extract a size x size matrix
    orig_matrix, lat_ind_list, lon_ind_list = get_matrix_centered_on(ds, lat_idx, lon_idx, window_size)

    # make a work copy of the matrix
    matrix = orig_matrix.copy()

    # define the halfsize
    halfsize = window_size // 2

    # debug print
    fullprint("find_next_through_classic_direction", "The extracted matrix is:", logFile)
    fullprint_matrix("find_next_through_classic_direction", matrix, logFile)
    
    checkDir = True
    while True:    
    
        # find the cells with the maximum value (mind the plural!!!)
        # (min_lat_rel, min_lon_rel), value = get_max_index(matrix)
        if len(directionList) > 10: # if we made the initialization
            coords_list, value = get_max_index(matrix, tolerance=0.1)
        else:
            coords_list, value = get_max_index(matrix, tolerance=0)
            
        # get the list of acceptable directions
        if len(directionList) > 0:
            dirs = get_acceptable_dir(directionList[-1])
        else:
            dirs = ["NW", "N", "NE", "E", "SE", "S", "SW", "W"]

        # check if the max value in the cell is NaN
        if np.isnan(value):
            fullprint("find_next_through_classic_direction", "Next element is NONE", logFile)
            return None, None

        # calculate trend to add it to the rank
        if len(directionList) > 10:
            trend = get_trend(directionList)
            dirs = get_acceptable_dir_by_trend(trend)

        # let's try to rank the points        
        ranking = []
        for p in coords_list:
            rank_new_el = {}
            rank_new_el["coords"] = p
            
            # get the direction of this element
            rank_new_el_local = [p[0] - window_size//2, p[1] - window_size // 2]
            rank_new_el["dir"] = get_direction_str(rank_new_el_local)    
            
            # add a score to the element based on the direction
            if len(directionList) > 0:
                rank_new_el["score"] = get_direction_rank(rank_new_el["dir"], directionList[-1])  
            else:
                rank_new_el["score"] = 9
            
            # add the element to the ranking 
            ranking.append(rank_new_el)
            
            if rank_new_el["dir"] in dirs:
                rank_new_el["score"] += 10

            
        # instead of extracting the first element, let's choose by rank
        max_element = max(ranking, key=lambda x: x["score"])
        next_el_coords = max_element["coords"]
        fullprint("find_next_through_classic_direction", "Ranking %s" % (ranking), logFile)
        fullprint("find_next_through_classic_direction", "--> Selected: %s" % max_element, logFile)

        next_el_value = value
        fullprint("find_next_through_classic_direction", "Candidate to be next element has value %s and coords %s" % (value, next_el_coords), logFile)
        
        # get the direction of this element
        local_next_el_coords = [next_el_coords[0] - window_size//2, next_el_coords[1] - window_size // 2]
        d = get_direction_str(local_next_el_coords)    
        
        # now check if the direction is compatible with the current path
        if checkDir:
                
            if not d in dirs:
                if len(directionList) > 0:
                    fullprint("find_next_through_classic_direction", "Direction %s IS NOT ok! Last was %s [last 5: %s] -- Modifying matrix..." % (d, directionList[-1], dirs), logFile)
                else:
                    fullprint("find_next_through_classic_direction", "Direction %s IS NOT ok! Last was None -- Modifying matrix..." % d, logFile)
                
                matrix[next_el_coords[0], next_el_coords[1]] = np.nan
                fullprint_matrix("find_next_through_classic_direction", matrix, logFile)
                if matrix.isnull().all():
                    matrix = orig_matrix.copy()
                    checkDir = False
                    
            else:
                if len(directionList) > 0:
                    fullprint("find_next_through_classic_direction", "Direction %s ok (last was %s)! -- [Last 5: %s]" % (d, directionList[-1], dirs), logFile)
                else:
                    fullprint("find_next_through_classic_direction", "Direction %s ok (last was None)!" % d, logFile)
                break
            
        else:
            break


    fullprint("find_next_through_classic_direction", "Selected element is %s with value %s" % (next_el_coords, next_el_value), logFile)

    # NOTE:
    # for the moment we just use the first element (we say it again)
    # (min_lat_rel, min_lon_rel) = coords_list[0]
    (min_lat_rel, min_lon_rel) = max_element["coords"]
    
    # get the global index of the new element
    local_lat_coords = range(0 - halfsize, 0 + halfsize + 1)
    local_lon_coords = range(0 - halfsize, 0 + halfsize + 1)
    lat_shift = local_lat_coords[min_lat_rel]
    lon_shift = local_lon_coords[min_lon_rel]
    shifted_lat = lat_idx + lat_shift
    shifted_lon = lon_idx + lon_shift
    
    # Update the current point to the one with minimum bathymetry
    #coords = [shifted_lat, shifted_lon]
    coords = [lat_shift, lon_shift]
    depth = get_depth(ds, (shifted_lat, shifted_lon))
    
    # return
    return depth, coords, d

        
#########################################################
#
# get_max_index function
#
#########################################################

def get_max_index(matrix, tolerance):

    """Return the index of the minimum bathymetry in the matrix.

    Parameters
    ----------
    matrix: np.matrix
        The 3x3 matrix where to look for the maximum
    tolerance: float
        The tolerance.. Set 0 to disable it
            
    Returns
    -------
    list
        a list of [lat,lon] elements with coordinates of the cells having the maximum value
    float
        the depth value for that points
    """
        
    # make a copy of the matrix, in order to round the decimal part
    rounded_matrix = np.round(matrix, decimals=2)
    
    # get the maximum
    maxValue = np.nanmax(rounded_matrix)
    
    # create a mask with all the values that are close to the maximum (using a tolerance threshold)
    mask = np.abs(rounded_matrix - maxValue) <= tolerance
    row_indices, col_indices = np.where(mask)
    indices_of_non_nan = list(zip(row_indices, col_indices))
    
    # find the cells having that value
    if np.isnan(maxValue):
        coords = np.argwhere(np.isnan(maxValue))
    else:
        coords = np.argwhere(rounded_matrix.values == maxValue)    

    # return
    # return coords, maxValue
    return indices_of_non_nan, maxValue


#########################################################
#
# get_depth function
#
#########################################################

def get_depth(ds, latlon_idx):
 
    """Return the index of the minimum bathymetry in the matrix.

    Parameters
    ----------
    ds: np.matrix
        The matrix where to look for the maximum
    latlon_idx: list
        A [lat,lon] structure

    Returns
    -------
    float
        the depth value for that point
    """
           
    depth = float(ds.bathy.isel(lat=latlon_idx[0], lon=latlon_idx[1]).values)
    if np.isnan(depth):
        return np.nan
    else:
        return np.round(depth, 2)
    

#########################################################
#
# get_3x3_centered_on function
#
#########################################################

def get_3x3_centered_on(ds, lat_idx, lon_idx):
    """Extract a 3x3 matrix centered on the given indices."""
    return ds.bathy.isel(lat=slice(lat_idx-1, lat_idx+2), lon=slice(lon_idx-1, lon_idx+2))


#########################################################
#
# get_matrix_centered_on function
#
#########################################################

def get_matrix_centered_on(ds, lat_idx, lon_idx, size):
  
    """Extract a size x size matrix centered on the given indices.

    Parameters
    ----------
    ds: np.matrix
        The original matrix
    lat_idx: int
        The latitude index of the center for the new matrix
    lon_idx: int
        The longitude index of the center for the new matrix
    size: int
        The size of the matrix (must be odd)
        
    Returns
    -------
    np.matrix
        the extracted submatrix
    """
    
    # check if size is odd. Cannot be even
    if (size % 2 == 0):
        raise Exception("matrix size cannot be even!")
    halfsize = size // 2
    
    # extract a matrix with the bathymetry and the corresponding matrix of indices
    matrix = ds.bathy.isel(lat=slice(lat_idx-halfsize, lat_idx+halfsize+1), lon=slice(lon_idx-halfsize, lon_idx+halfsize+1))
    matrix_ind = [(l1, l2) for l1 in range(lat_idx-halfsize, lat_idx+halfsize+1) for l2 in range(lon_idx-halfsize, lon_idx+halfsize+1)]
    lats_ind = range(lat_idx-halfsize, lat_idx+halfsize+1)
    lons_ind = range(lon_idx-halfsize, lon_idx+halfsize+1)

    # return the matrix and two arrays (lat and lon)
    return matrix, lats_ind, lons_ind