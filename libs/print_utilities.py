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


# #########################################################
# #
# # print_matrix
# #
# #########################################################

# def print_matrix(matrix, logFile=None):
  
#     """Just an handler to have a clear/simplified view of a matrix
    
#     Parameters
#     ----------
#     matrix: np.matrix
#         a numpy matrix
#     logFile: fileDescriptor
#         a descriptor for the log file

#     Returns
#     -------
#     bool
#         nothing to declare.. :-)
#     """

#     inv_matrix = matrix[::-1]
    
#     for i in range(inv_matrix.shape[0]):
#         for j in range(inv_matrix.shape[1]):
#             strval = str(np.round(inv_matrix[i,j].values, 2)).ljust(4)
#             print("%s\t\t" % strval, end='')          
            
#         print()
        
    
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
    
    
#########################################################
#
# fullprint
#
#########################################################

def fullprint(header, text, logFile=None, newline=True, error=False):
  
    """Just an handler to have a symbolic view of the zonal direction
    
    Parameters
    ----------
    text: string
        a list made by an int for lon shift, one for lat shift
    logFile: fileDescriptor
        the file descriptor of our log file
        
    """
    
    # set the color
    if error:
        color = "red"
    else:
        color = "blue"
    
    # write on console and log
    if newline:
        
        # write on screen
        print(colored(header, color, attrs=["bold"]) + " --- %s" % text)
        
        # write on log
        if logFile:
            logFile.write(text)
            logFile.write("\n")
        
        
    else:
        
        # write on screen
        print(colored(header, color, attrs=["bold"]) + " --- %s" % text, end='')

        # write on log
        if logFile:
            logFile.write(text)
    
    
    
#########################################################
#
# fullprint_matrix
#
#########################################################

def fullprint_matrix(header, matrix, logFile=None):
  
    """A modified version of fullprint to deal with a matrix
    
    Parameters
    ----------
    matrix: np.matrix
        a numpy matrix
    logFile: fileDescriptor
        a descriptor for the log file
        
    """

    inv_matrix = matrix[::-1]
    
    for i in range(inv_matrix.shape[0]):
        
        # print the line number
        print("[LINE %s]\t\t" % str(inv_matrix.shape[0] - i - 1), end='')          
        # print on log
        if logFile:
            logFile.write("[LINE %s]\t\t" % str(inv_matrix.shape[0] - i - 1))
    
        for j in range(inv_matrix.shape[1]):
            strval = str(np.round(inv_matrix[i,j].values, 2)).ljust(4)
            
            # print on console
            print("%s\t\t" % strval, end='')          
            
            # print on log
            if logFile:
                logFile.write("%s\t\t" % strval)          

        # add the newline
        print()
        if logFile:
            logFile.write("\n")