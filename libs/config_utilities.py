#!/usr/bin/env python3

# global reqs
from configparser import *
import sys

# local reqs
from libs.exceptions import *

    
#########################################################
#
# read_config
#
#########################################################

def read_config(configFile):
    
    """Reads the config file

    Parameters
    ----------
    configFile: string
        The full path to the configuration file
    
    Returns
    -------
    dict
        a dictionary with the configuration
    """    
    
    # initialize a data structure
    configDict = {}
    
    # create a parser and parse the file
    config = ConfigParser()
    config.read(configFile)
    
    # read all the sections
    read_algorithm_section(config, configDict)
    read_plot_section(config, configDict)
    read_output_section(config, configDict)
    read_debug_section(config, configDict)
    
    # return
    return configDict
    
 
def read_algorithm_section(config, configDict):
    
    """Reads the algorithm section of the configuration file

    Parameters
    ----------
    config: ConfigParser
        A configParser object
    configDict: dict
        The current dictionary
    
    """    
    
    # try to read the window size
    try:
        configDict["windowSize"] = config.getint("Algorithm", "WindowSize")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'WindowSize' option in 'Algorithm' section of configuration file!")
        sys.exit(22)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(20)

    # try to read the start lat
    try:
        configDict["startLat"] = config.getfloat("Algorithm", "StartLat")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'StartLat' option in 'Algorithm' section of configuration file!")
        sys.exit(23)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(20)

    # try to read the start lon
    try:
        configDict["startLon"] = config.getfloat("Algorithm", "StartLon")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'StartLon' option in 'Algorithm' section of configuration file!")
        sys.exit(24)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(20)

    # try to read the end lat
    try:
        configDict["endLat"] = config.getfloat("Algorithm", "EndLat")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'EndLat' option in 'Algorithm' section of configuration file!")
        sys.exit(25)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(20)

    # try to read the end lon
    try:
        configDict["endLon"] = config.getfloat("Algorithm", "EndLon")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'EndLon' option in 'Algorithm' section of configuration file!")
        sys.exit(26)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(20)
        
    # try to read the start lat
    try:
        configDict["startDir"] = config.get("Algorithm", "StartDir")
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'StartDir' option in 'Algorithm' section of configuration file!")
        sys.exit(21)
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Algorithm' section of configuration file!")
        sys.exit(20)

    
        
def read_plot_section(config, configDict):
    
    """Reads the algorithm section of the configuration file

    Parameters
    ----------
    config: ConfigParser
        A configParser object
    configDict: dict
        The current dictionary
    
    """    
    
    # read the point sparsity value
    try:
        configDict["pointSparsity"] = config.getint("Plot", "PointSparsity")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointSparsity' option in 'Plot' section of configuration file!")
        sys.exit(31)

    # read the pointsEnabled
    try:
        configDict["pointsEnabled"] = config.getboolean("Plot", "PointsEnabled")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointsEnabled' option in 'Plot' section of configuration file!")
        sys.exit(32)
    
    # read the lablesEnabled
    try:
        configDict["labelsEnabled"] = config.getboolean("Plot", "LabelsEnabled")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LabelsEnabled' option in 'Plot' section of configuration file!")
        sys.exit(33)
    
    # read the pointsSize
    try:
        configDict["pointsSize"] = config.getfloat("Plot", "PointsSize")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PointsSize' option in 'Plot' section of configuration file!")
        sys.exit(34)
 
    # read the labelsSize
    try:
        configDict["labelsSize"] = config.getfloat("Plot", "LabelsSize")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LabelsSize' option in 'Plot' section of configuration file!")
        sys.exit(35)

    # read the latMin
    try:
        configDict["latMin"] = config.getfloat("Plot", "LatMin")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LatMin' option in 'Plot' section of configuration file!")
        sys.exit(36)

    # read the latMax
    try:
        configDict["latMax"] = config.getfloat("Plot", "LatMax")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LatMax' option in 'Plot' section of configuration file!")
        sys.exit(37)

    # read the lonMin
    try:
        configDict["lonMin"] = config.getfloat("Plot", "LonMin")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LonMin' option in 'Plot' section of configuration file!")
        sys.exit(38)
    
    # read the lonMax
    try:
        configDict["lonMax"] = config.getfloat("Plot", "LonMax")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LonMax' option in 'Plot' section of configuration file!")
        sys.exit(39)                    

    # read the plotsteps
    try:
        configDict["plotSteps"] = config.getboolean("Plot", "PlotSteps")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Plot' section of configuration file!")
        sys.exit(30)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PlotSteps' option in 'Plot' section of configuration file!")
        sys.exit(40)                    


def read_output_section(config, configDict):
    
    """Reads the output section of the configuration file

    Parameters
    ----------
    config: ConfigParser
        A configParser object
    configDict: dict
        The current dictionary
    
    """    
    
    # read the name of the directory for plots   
    try:
        configDict["plotDirectory"] = config.get("Output", "PlotDirectory")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(50)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PlotDirectory' option in 'Output' section of configuration file!")
        sys.exit(51)

    # read the name of the baseline file
    try:
        configDict["baselinePlotName"] = config.get("Output", "BaselinePlotName")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(50)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'BaselinePlotName' option in 'Output' section of configuration file!")
        sys.exit(52)


    # read the name of the log file
    try:
        configDict["logFile"] = config.get("Output", "LogFile")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(50)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'LogFile' option in 'Output' section of configuration file!")
        sys.exit(53)

    # read the name of the log file
    try:
        configDict["outputDirectory"] = config.get("Output", "OutputDirectory")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(50)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'OutputDirectory' option in 'Output' section of configuration file!")
        sys.exit(54)
        
    # read the name of the thalweg file
    try:
        configDict["thalwegFile"] = config.get("Output", "ThalwegFile")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Output' section of configuration file!")
        sys.exit(50)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'ThalwegFile' option in 'Output' section of configuration file!")
        sys.exit(55)
        
        
def read_debug_section(config, configDict):
    
    """Reads the debug section of the configuration file

    Parameters
    ----------
    config: ConfigParser
        A configParser object
    configDict: dict
        The current dictionary
    
    """     

    # read the plotStartPoint, if any
    try:
        configDict["plotStartPoint"] = config.getint("Debug", "PlotStartPoint")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Debug' section of configuration file!")
        sys.exit(60)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PlotStartPoint' option in 'Debug' section of configuration file!")
        sys.exit(61)

    # read the plotEndPoint, if any
    try:
        configDict["plotEndPoint"] = config.getint("Debug", "PlotEndPoint")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Debug' section of configuration file!")
        sys.exit(60)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'PlotEndPoint' option in 'Debug' section of configuration file!")
        sys.exit(62)
        
    # read the thalwegStop
    try:
        configDict["thalwegStop"] = config.getint("Debug", "ThalwegStop")
    except NoSectionError:
        raise IncompleteConfigFileError("Missing 'Debug' section of configuration file!")
        sys.exit(60)
    except NoOptionError:
        raise IncompleteConfigFileError("Missing 'ThalwegStop' option in 'Debug' section of configuration file!")
        sys.exit(63)
        