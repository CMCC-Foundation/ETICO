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
from configparser import *

# local reqs
from libs.print_utilities import *
from libs.exceptions import *

    
#########################################################
#
# read_config
#
#########################################################

def read_config(configFile):
    
    """Identifies the next element through the zonal direction

    Parameters
    ----------
    configFile: string
        The full path to the configuration file
    
    Returns
    -------
    dict
        a dictionary with the configuration
    """    
    
    # debug print
    print(colored("libs::config_utilities::read_config", "blue", attrs=["bold"]) + " --- Method starting")

    # initialize a data structure
    configDict = {}
    
    # create a parser and parse the file
    config = ConfigParser()
    config.read(configFile)
    
    ###########################################
    #
    # algorithm section
    #
    ###########################################
    
    # read the max search algo         
    try:
        configDict["maxSearchAlgo"] = config.get("Algorithm", "MaxSearchAlgo")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'MaxSearchAlgo' option in 'Algorithm' section of configuration file!")
        sys.exit(2)
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(3)
    
    # try to read the window size
    try:
        configDict["windowSize"] = config.getint("Algorithm", "WindowSize")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'WindowSize' option in 'Algorithm' section of configuration file!")
        sys.exit(4)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(3)
        
    if not configDict["maxSearchAlgo"] in ["Zonal", "Classic"]:
        raise UnsupportedMaxSearchAlgoError()
        sys.exit(5)
     
    ###########################################
    #
    # plot section
    #
    ###########################################       

    # read the point sparsity value
    try:
        configDict["pointSparsity"] = config.getint("Plot", "PointSparsity")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointSparsity' option in 'Plot' section of configuration file!")
        sys.exit(7)

    # read the pointsEnabled
    try:
        configDict["pointsEnabled"] = config.getboolean("Plot", "PointsEnabled")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointsEnabled' option in 'Plot' section of configuration file!")
        sys.exit(8)
    
    # read the lablesEnabled
    try:
        configDict["labelsEnabled"] = config.getboolean("Plot", "LabelsEnabled")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LabelsEnabled' option in 'Plot' section of configuration file!")
        sys.exit(9)
    
    # read the pointsSize
    try:
        configDict["pointsSize"] = config.getfloat("Plot", "PointsSize")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointsSize' option in 'Plot' section of configuration file!")
        sys.exit(10)
 
    # read the labelsSize
    try:
        configDict["labelsSize"] = config.getfloat("Plot", "LabelsSize")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LabelsSize' option in 'Plot' section of configuration file!")
        sys.exit(11)
    
    # return
    return configDict