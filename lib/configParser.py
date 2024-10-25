#!/usr/bin/python3

################################################
#
# requirements
#
################################################        

# global requirements
import logging
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
    config = {'Output': {}, 'Input': {}}
    
    # Validate and extract parameters from the Output section
    try:
        config['Output']['baseFolder'] = parser.get('Output', 'baseFolder')
        if not config['Output']['baseFolder']:
            raise ValueError("The 'baseFolder' entry in the 'Output' section is empty.")
    except (NoSectionError, NoOptionError) as e:
        logging.error(f"Missing required parameter: {e}")
        raise
    except ValueError as e:
        logging.error(e)
        raise
    
    # validate and extract parameters from the Input section
    try:

        # read the name for the base output folder
        config['Output']['baseFolder'] = parser.get('Output', 'baseFolder')
        if not config['Output']['baseFolder']:
            raise ValueError("The 'baseFolder' entry in the 'Output' section is empty.")

        # read the name for the base output folder
        config['Output']['dotSize'] = parser.getfloat('Output', 'dotSize')
        if not config['Output']['dotSize']:
            raise ValueError("The 'dotSize' entry in the 'Output' section is empty.")
        
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
