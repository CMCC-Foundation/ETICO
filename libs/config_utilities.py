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
    
    # read the max search algo         
    try:
        configDict["maxSearchAlgo"] = config.get("Algorithm", "MaxSearchAlgo")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'MaxSearchAlgo' option in 'Algorithm' section of configuration file!")
        sys.exit(1)
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(1)
    
    # try to read the window size
    try:
        configDict["windowSize"] = config.getint("Algorithm", "WindowSize")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'WindowSize' option in 'Algorithm' section of configuration file!")
        sys.exit(1)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(1)
        
    if not configDict["maxSearchAlgo"] in ["Zonal", "Classic"]:
        raise UnsupportedMaxSearchAlgoError()
        sys.exit(1)
        
    # return
    return configDict