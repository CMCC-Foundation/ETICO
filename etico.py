#!/usr/bin/python3

################################################
#
# requirements
#
################################################

# global requirements
import logging
import sys
import os

# local requirements
from lib.configParser import *
from lib.explorer import *
from lib.plot import *


################################################
#
# logging configuration
#
################################################

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


################################################
#
# Main
#
################################################

if __name__ == "__main__":
    
    ################################################
    #
    # input parameters
    #
    ################################################
    
    if len(sys.argv) < 2:
        logging.error("No configuration file specified. Please provide the path to the configuration file.")
        sys.exit(1)

    config_file = sys.argv[1]
    logging.info(f"Reading configuration file: {config_file}")
    
    try:
        config = parse_config(config_file)
        logging.info("Configuration file parsed successfully.")
        # You can now use the parsed config for further processing
        # Example:
        logging.info(f"Base Folder: {config['Output']['baseFolder']}")
        logging.info(f"Input File: {config['Input']['inputFile']}")
        logging.info(f"Window Size: {config['Input']['windowSize']}")
        
    except Exception as e:
        logging.error(f"Error while parsing the configuration file: {e}")
        sys.exit(1)


    ################################################
    #
    # create output folder
    #
    ################################################
        
    # create the baseFolder if it does not exist
    base_folder = config['Output']['baseFolder']
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
        logging.info(f"Created base folder: {base_folder}")
    else:
        logging.info(f"Base folder already exists: {base_folder}")
        
        
    ################################################
    #
    # run the algorithm
    #
    ################################################

    ds = load_netcdf(config['Input']['inputFile'])
    find_highest_bathy(ds, config,
                       start_lat=config['Input']['startLat'],
                       start_lon=config['Input']['startLon'],
                       window_size=config['Input']['windowSize'],
                       max_iterations=config['Input']['maxIterations'],
                       depth_tolerance=config['Input']['depthTolerance'],
                       init_phase=config['Input']['initPhase'],                       
                       start_direction=config['Input']['initialDirection'],
                       output_directory=config['Output']['baseFolder'])


    ################################################
    #
    # plot data
    #
    ################################################

    plot_bathy_with_path(config['Input']['inputFile'],
                         os.path.join(config['Output']['baseFolder'], "path.csv"),
                         os.path.join(config['Output']['baseFolder'], "thalweg.png"),
                         config)
