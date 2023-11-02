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

    # read the latMin
    try:
        configDict["latMin"] = config.getfloat("Plot", "LatMin")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LatMin' option in 'Plot' section of configuration file!")
        sys.exit(19)

    # read the latMax
    try:
        configDict["latMax"] = config.getfloat("Plot", "LatMax")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LatMax' option in 'Plot' section of configuration file!")
        sys.exit(20)

    # read the lonMin
    try:
        configDict["lonMin"] = config.getfloat("Plot", "LonMin")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LonMin' option in 'Plot' section of configuration file!")
        sys.exit(21)
 
    # read the lonMax
    try:
        configDict["lonMax"] = config.getfloat("Plot", "LonMax")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LonMax' option in 'Plot' section of configuration file!")
        sys.exit(22)                    

    # read the plotsteps
    try:
        configDict["plotSteps"] = config.getboolean("Plot", "PlotSteps")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(6)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PlotSteps' option in 'Plot' section of configuration file!")
        sys.exit(23)                    


    ###########################################
    #
    # output section
    #
    ###########################################
    
    # read the name of the directory for plots   
    try:
        configDict["plotDirectory"] = config.get("Output", "PlotDirectory")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(12)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PlotDirectory' option in 'Output' section of configuration file!")
        sys.exit(13)

    # read the name of the baseline file
    try:
        configDict["baselinePlotName"] = config.get("Output", "BaselinePlotName")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(12)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'BaselinePlotName' option in 'Output' section of configuration file!")
        sys.exit(14)


    # read the name of the log file
    try:
        configDict["logFile"] = config.get("Output", "LogFile")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(12)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LogFile' option in 'Output' section of configuration file!")
        sys.exit(15)


    # read the name of the log file
    try:
        configDict["outputDirectory"] = config.get("Output", "OutputDirectory")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(12)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'OutputDirectory' option in 'Output' section of configuration file!")
        sys.exit(16)
        
        
    ###########################################
    #
    # debug section
    #
    ###########################################       

    # read the plotStartPoint, if any
    try:
        configDict["plotStartPoint"] = config.getint("Debug", "PlotStartPoint")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Debug' section of configuration file!")
        sys.exit(18)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointSparsity' option in 'Plot' section of configuration file!")
        sys.exit(16)

    # read the plotEndPoint, if any
    try:
        configDict["plotEndPoint"] = config.getint("Debug", "PlotEndPoint")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Debug' section of configuration file!")
        sys.exit(18)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointsEnabled' option in 'Plot' section of configuration file!")
        sys.exit(17)
        
    # read the thalwegStop
    try:
        configDict["thalwegStop"] = config.getint("Debug", "ThalwegStop")
    except NoSectionError:
        print(traceback.print_exc())
        raise IncompleteConfigFileError("Missing 'Debug' section of configuration file!")
        sys.exit(18)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'ThalwegStop' option in 'Plot' section of configuration file!")
        sys.exit(24)

    ###########################################
    #
    # return
    #
    ###########################################

    # return
    return configDict
 