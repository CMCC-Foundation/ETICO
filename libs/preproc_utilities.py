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
import scipy

# local reqs
from libs.print_utilities import *


 
#########################################################
#
# find_starting_point
#
#########################################################

def find_baseline(ds):
    
    """Identifies the starting point for the thalweg

    Parameters
    ----------
    ds: xarray.core.dataset.Dataset
        The full dataset 

    Returns
    -------
    numpy.ndarray
        the matrix containing the baseline (a 1/np.nan matrix)
    """
    
    # debug print
    print(colored("libs::preproc_utilities::find_baseline", "blue", attrs=["bold"]) + " --- Method starting")

    #################################################################
    #
    # GET THE CONTOUR
    # 
    #################################################################
    
    # Define a 3x3 kernel for convolution
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
     
    # Identify NaN values in the matrix, then create a mask where nan is replaced by 1, 0 elsewhere 
    nan_mask = np.isnan(ds.bathy)
    binary_mask = nan_mask.astype(int)
     
    # Convolve the binary mask with the kernel (each cell will have as the value the number of
    # surrounding elements equal to nan)
    surrounded_mask = scipy.signal.convolve2d(binary_mask, kernel, mode='same', boundary="wrap")
     
    # convert surrounded_mask to a structure compliant with matrix
    # by setting np.nan where the mask is not 0, keep the value elsewhere
    manip_mask = surrounded_mask.copy()
    manip_mask = np.where(manip_mask == 8, np.nan, manip_mask) # points on the land
    manip_mask = np.where(manip_mask == 0, np.nan, manip_mask) # points inside the river
    manip_mask = np.where(manip_mask >= 0, 1, manip_mask)      # points on the edge
     
     
    #################################################################
    #
    # HORIZONTAL SCAN
    # 
    #################################################################
     
    # 0 - initialize data structure
    output_matrix_vert = np.zeros(manip_mask.shape)
    output_matrix_hori = np.zeros(manip_mask.shape)
     
    # 1 - perform a top-down scan
    # Iterate through each column
    for col in range(manip_mask.shape[1]):
        first_non_zero_index = np.argmax(manip_mask[:, col] == 1)
        val = manip_mask[first_non_zero_index, col]
        output_matrix_vert[first_non_zero_index, col] = val
    
    # 2 - perform a left-right0scan
    for row in range(manip_mask.shape[0]):
        first_non_zero_index = np.argmax(manip_mask[row, :] == 1)
        val = manip_mask[row, first_non_zero_index]
        output_matrix_hori[row, first_non_zero_index] = val
    
    # 3 - mix the two
    output_matrix = np.logical_or(output_matrix_hori, output_matrix_vert)
    output_matrix_with_nan = np.where(output_matrix == 0, np.nan, output_matrix)
     
    # # 4 - identify gaps through another convolution
        
    # we compare the FULL_EDGE matrix with the SCAN_MATRIX
    # for each element in the matrix that is 1 we build a neighborhood matrix
    # and if the neighborhood of the two matrices is different, we copy the
    # neighborhood of the FULL_EDGE on the SCAN_MATRIX 
    scan_matrix = output_matrix_with_nan.copy()
    full_matrix = manip_mask.copy()
    
    # Get the dimensions of the matrices
    rows, cols = scan_matrix.shape
    
    # Define the neighborhood size (3x3)
    neighborhood_size = (3, 3)
    
    # Iterate over each element in scan_matrix
    for i in range(rows):
        for j in range(cols):
            
            # Check if the current element in scan_matrix is 1
            if scan_matrix[i, j] == 1:
                
                # Extract the 3x3 neighborhood from both full_matrix and scan_matrix
                full_neighborhood = full_matrix[i - 1:i + 2, j - 1:j + 2]
                scan_neighborhood = scan_matrix[i - 1:i + 2, j - 1:j + 2]
                
                # Compare the neighborhoods
                if not np.array_equal(full_neighborhood, scan_neighborhood):
                    
                    # Copy the full_matrix neighborhood to scan_matrix
                    scan_matrix[i - 1:i + 2, j - 1:j + 2] = full_neighborhood
        

    # return the baseline
    return scan_matrix


#########################################################
#
# find_starting_point
#
#########################################################

def find_starting_points(ds):
    
    """Identifies the starting point for the thalweg

    Parameters
    ----------
    ds: xarray.core.dataset.Dataset
        The full dataset 

    Returns
    -------
    list
        a list of starting points
    """
    
    # debug print
    print(colored("libs::preproc_utilities::find_starting_points", "blue", attrs=["bold"]) + " --- Method starting")
   
    # horizontal scan
    # -- finds the first line where there is a non null element
    # -- finds the last line where there is a non null element
    firstRow = 0
    for n in ds.bathy.values:
        if not np.isnan(n).all():
            break
        firstRow += 1
        
    first_row = np.argmax(~np.isnan(ds.bathy.values), axis=0).min()
    last_row = np.argmax(~np.isnan(ds.bathy.values[::-1, :]), axis=0).min()
    
    # # Adjust indices for reversed arrays
    # last_row = bathymetry.shape[0] - last_row - 1
    # last_col = bathymetry.shape[1] - last_col - 1    

    # vertical scan
    # -- finds the first line where there is a non null element
    # -- finds the last line where there is a non null element
    firstCol = 0
    for n in range(ds.bathy.shape[1]):
        if not np.isnan(ds.bathy.values[:,n]).all():
            break
        firstCol += 1
        
    pdb.set_trace()