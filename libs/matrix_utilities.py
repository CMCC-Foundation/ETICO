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

def get_zonal_direction(matrix, lats, lons):
    
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
        a list containing the shift on lon and lat for the zonal direction:
        -1,-1 (NW)   -1,0 (N)   -1,1 (NE)
         0,-1 (W)                0,1 (E)
         1,-1 (SW)    1,0 (S)    1,1 (SE)
    """
    
    # debug print
    print(colored("libs::matrix_utilities::get_zonal_direction", "blue", attrs=["bold"]) + " --- Method starting")
    print_matrix(matrix)
    
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
    print(colored("libs::matrix_utilities::get_zonal_direction", "blue", attrs=["bold"]) + " --- Resampled matrix is:")
    print(final_matrix)
    coords,value = find_max(final_matrix)
    zd = [coords[0]-1, coords[1]-1]
    print(colored("libs::matrix_utilities::get_zonal_direction", "blue", attrs=["bold"]) + " --- Zonal direction is %s,%s %s" % (zd[0], zd[1], print_zonal_direction(zd)))

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

def find_next_through_zonal_direction(matrix, coords, lon_idx, lat_idx):
    
    """Extract the max from the 3 elements of the matrix identified by zonal direction

    Parameters
    ----------
    matrix: np.matrix
        The 3x3 matrix where to look for the maximum
    coords: list
        The lat and lon indices identifying the zonal direction

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
            
    print(colored("libs::matrix_utilities::find_next_through_zonal_direction", "blue", attrs=["bold"]) + " --- Returning %s, %s" % (max_value, max_coords))
    return max_value, max_coords
            
    
#########################################################
#
# get_min_index function
#
#########################################################

def get_min_index(matrix):

    """Return the index of the minimum bathymetry in the matrix.

    Parameters
    ----------
    matrix: np.matrix
        The 3x3 matrix where to look for the maximum

    Returns
    -------
    list
        a [lat,lon] structure with coordinates of the min element
    float
        the depth value for that point
    """
        
    # get the minimum
    try:
        coords = np.unravel_index(np.nanargmax(matrix), matrix.shape)
    except ValueError:
        return None, None, None

    # check if nan
    if np.isnan(matrix[coords]):
        return coords, None
    
    print("[get_min_index] === Returning %s, %s" % (coords, matrix[coords].values))
    return coords, matrix[coords].values


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