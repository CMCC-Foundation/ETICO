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
from lib.postproc import *
from lib.explorer import *
from lib.astar import *
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
    # run the greedy algorithm (needed for H function)
    #
    ################################################

    start_a_star(config)
        
        
    ################################################
    #
    # run the algorithm
    #
    ################################################

    ds = load_netcdf(config['Input']['inputFile'])

    # intialise restart flag and counter
    restart_points = []
    restart = True
    rest_cnt = 0

    # loop
    while restart:

        # invoke the algorithm
        if rest_cnt == 0:
            restart, current_lat, current_lon, lastDirection, iteration = find_highest_bathy(ds, config)
            logging.info(colored(f"=== RESTART {restart} ===", "blue", attrs=["bold"]))
        else:
            logging.info(colored(f"=== RESTART {restart} ===", "yellow", attrs=["bold"]))
            if restart == True:
                logging.info(colored(f"=== RESTART AT {iteration}, #{rest_cnt} ===", "red", attrs=["bold"]))
                logging.info(colored(f"=== RESTARTING AT {current_lat}, {current_lon} IN DIRECTION {lastDirection} ===", "red", attrs=["bold"]))            
                input()
                restart, current_lat, current_lon, lastDirection, iteration = find_highest_bathy(ds, config, current_lat, current_lon, lastDirection, iteration)
                restart_points.append(iteration)                
            
        rest_cnt += 1

        # stop after 3 iterations
        if rest_cnt == 3:
            break

        
    ################################################
    #
    # run the postprocessing
    #
    ################################################

    postproc(config)

    
    ################################################
    #
    # plot data
    #
    ################################################

    plot_bathy_with_path(config)


    # todo LIST
    # - post processing procedure to identify and remove loops
    # - implement a restart algorithm, to restart the algo from the last point if the
    #   end point was not reached
    # - add a friendly name for the "Experiment" so that it can be used for names of files and dirs
    # - change the format of logs
    # - plot the riverbed profile
    # - check the scoring functions
    # - make the scoring functions plug and play
