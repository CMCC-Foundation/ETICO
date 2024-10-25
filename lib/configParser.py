#!/usr/bin/python3

################################################
#
# requirements
#
################################################        

# global requirements
import logging
import traceback
from configparser import ConfigParser, NoSectionError, NoOptionError


################################################
#
# logger configuration
#
################################################        

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


################################################
#
# parse_config function
#
################################################        

def parse_config(config_file):
    
    parser = ConfigParser()
    parser.read(config_file)
    
    # initialise a dictionary to hold the configuration
    config = {'Output': {}, 'Input': {}, 'Plot': {}}

    # validate and extract parameters from the Input section
    try:

        ### Output section
        
        # read the name for the base output folder
        config['Output']['baseFolder'] = parser.get('Output', 'baseFolder')
        if not config['Output']['baseFolder']:
            raise ValueError("The 'baseFolder' entry in the 'Output' section is empty.")
        
        # read the name for the thalweg csv file
        config['Output']['thalwegCsvFile'] = parser.get('Output', 'thalwegCsvFile')
        if not config['Output']['thalwegCsvFile']:
            raise ValueError("The 'thalwegCsvFile' entry in the 'Output' section is empty.")
                
        # read the name for the thalweg png file
        config['Output']['thalwegPngFile'] = parser.get('Output', 'thalwegPngFile')
        if not config['Output']['thalwegPngFile']:
            raise ValueError("The 'thalwegPngFile' entry in the 'Output' section is empty.")

        
        ### Plot section
        
        # read the size of the dots to plot
        config['Plot']['dotSize'] = parser.get('Plot', 'dotSize')
        if not config['Plot']['dotSize']:
            raise ValueError("The 'dotSize' entry in the 'Plot' section is empty.")

        # read whether or not to plot dots
        config['Plot']['plotDots'] = parser.getboolean('Plot', 'plotDots')
        if not config['Plot']['plotDots']:
            raise ValueError("The 'plotDots' entry in the 'Plot' section is empty.")

        # read the interval to plot dots
        config['Plot']['dotsInterval'] = parser.getint('Plot', 'dotsInterval')
        if not config['Plot']['dotsInterval']:
            raise ValueError("The 'dotsInterval' entry in the 'Plot' section is empty.")

        # read the font size for the dots label
        config['Plot']['dotsFontSize'] = parser.getint('Plot', 'dotsFontSize')
        if not config['Plot']['dotsFontSize']:
            raise ValueError("The 'dotsFontSize' entry in the 'Plot' section is empty.")

        # read the font colour for the dots label
        config['Plot']['dotsFontColour'] = parser.get('Plot', 'dotsFontColour')
        if not config['Plot']['dotsFontColour']:
            raise ValueError("The 'dotsFontColour' entry in the 'Plot' section is empty.")

        # read the size for the start point
        config['Plot']['startPointSize'] = parser.getint('Plot', 'startPointSize')
        if not config['Plot']['startPointSize']:
            raise ValueError("The 'startPointSize' entry in the 'Plot' section is empty.")

        # read the marker to use for the start point
        config['Plot']['startPointMarker'] = parser.get('Plot', 'startPointMarker')
        if not config['Plot']['startPointMarker']:
            raise ValueError("The 'startPointMarker' entry in the 'Plot' section is empty.")

        # read the colour for the start point
        config['Plot']['startPointColour'] = parser.get('Plot', 'startPointColour')
        if not config['Plot']['startPointColour']:
            raise ValueError("The 'startPointColour' entry in the 'Plot' section is empty.")

        # read the size for the end point
        config['Plot']['endPointSize'] = parser.getint('Plot', 'endPointSize')
        if not config['Plot']['endPointSize']:
            raise ValueError("The 'endPointSize' entry in the 'Plot' section is empty.")

        # read the marker to use for the end point
        config['Plot']['endPointMarker'] = parser.get('Plot', 'endPointMarker')
        if not config['Plot']['endPointMarker']:
            raise ValueError("The 'endPointMarker' entry in the 'Plot' section is empty.")

        # read the colour for the end point
        config['Plot']['endPointColour'] = parser.get('Plot', 'endPointColour')
        if not config['Plot']['endPointColour']:
            raise ValueError("The 'endPointColour' entry in the 'Plot' section is empty.")      

        
        ### Input section
        
        # read the name for the input file (.grd, .nc, etc)
        config['Input']['inputFile'] = parser.get('Input', 'inputFile')
        if not config['Input']['inputFile']:
            raise ValueError("The 'inputFile' entry in the 'Input' section is empty.")

        # read the size of the window for the algorithm
        config['Input']['windowSize'] = parser.getint('Input', 'windowSize')
        if config['Input']['windowSize'] <= 0:
            raise ValueError("The 'windowSize' must be a positive integer.")

        # read latitude of the starting point
        config['Input']['startLat'] = parser.getfloat('Input', 'startLat')
        if not (-90 <= config['Input']['startLat'] <= 90):
            raise ValueError("The 'startLat' must be within the range -90 to 90 degrees.")

        # read longitude of the starting point        
        config['Input']['startLon'] = parser.getfloat('Input', 'startLon')
        if not (-180 <= config['Input']['startLon'] <= 180):
            raise ValueError("The 'startLon' must be within the range -180 to 180 degrees.")

        # read latitude of the ending point
        config['Input']['endLat'] = parser.getfloat('Input', 'endLat')
        if not (-90 <= config['Input']['endLat'] <= 90):
            raise ValueError("The 'endLat' must be within the range -90 to 90 degrees.")

        # read longitude of the ending point        
        config['Input']['endLon'] = parser.getfloat('Input', 'endLon')
        if not (-180 <= config['Input']['endLon'] <= 180):
            raise ValueError("The 'endLon' must be within the range -180 to 180 degrees.")

        # read Distancegitude of the ending point        
        config['Input']['endDistance'] = parser.getint('Input', 'endDistance')
        if not config['Input']['endDistance']:
            raise ValueError("The 'endDistance' entry in the 'Input' section is empty.")
        
        # read the initial direction
        config['Input']['initialDirection'] = parser.get('Input', 'initialDirection')
        if not config['Input']['initialDirection']:
            raise ValueError("The 'initialDirection' entry in the 'Input' section is empty.")

        # read the maximum number of iterations
        config['Input']['maxIterations'] = parser.getint('Input', 'maxIterations')
        if not config['Input']['maxIterations']:
            raise ValueError("The 'maxIterations' entry in the 'Input' section is empty.")

        # read the length of the initialisation phase
        config['Input']['initPhase'] = parser.getint('Input', 'initPhase')
        if not config['Input']['initPhase']:
            raise ValueError("The 'initPhase' entry in the 'Input' section is empty.")

        # read the depth tolerance
        config['Input']['depthTolerance'] = parser.getfloat('Input', 'depthTolerance')
        if not config['Input']['depthTolerance']:
            raise ValueError("The 'depthTolerance' entry in the 'Input' section is empty.")
        
        # read the name of the input file (netCDF, grd, etc..)
        config['Input']['inputFile'] = parser.get('Input', 'inputFile')
        if not config['Input']['inputFile']:
            raise ValueError("The 'inputFile' entry in the 'Input' section is empty.")

        # read the size of the window for the algorithm
        config['Input']['windowSize'] = parser.getint('Input', 'windowSize')
        if config['Input']['windowSize'] <= 0:
            raise ValueError("The 'windowSize' must be a positive integer.")
        
    except (NoSectionError, NoOptionError) as e:
        logging.error(f"Missing required parameter: {e}")
        raise
    except ValueError as e:
        logging.error(e)
        raise

    # return the configuration dictionary
    return config
