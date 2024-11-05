#!/usr/bin/python3

################################################
#
# requirements
#
################################################

# global requirements
import xarray as xr
import pandas as pd
import numpy as np
import sys
import os
import pdb
import csv
import math
import logging
import traceback
from termcolor import colored
from collections import Counter
from tabulate import tabulate
from math import radians, cos, sin, sqrt, atan2


################################################
#
# log configuration
#
################################################

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


################################################
#
# postproc
#
################################################

def postproc(config):

    # open the thalweg CSV file
    csv_file = os.path.join(config["Output"]["baseFolder"], config['Output']['thalwegCsvFile'])

    # open the NetCDF file
    netcdf_file = config["Input"]["inputFile"]

    # load the CSV file
    df = pd.read_csv(csv_file)

    # load the NetCDF file
    dataset = xr.open_dataset(netcdf_file)
    bathy = dataset.variables['bathy'][:]
    latitudes = dataset.variables['lat'][:]
    longitudes = dataset.variables['lon'][:]

    # prepare a list to store results for the new CSV
    results = []

    # helper function to find indices for the neighborhood
    def find_index(lat, lon):
        lat_idx = (np.abs(latitudes - lat)).argmin()
        lon_idx = (np.abs(longitudes - lon)).argmin()
        return int(lat_idx.values), int(lon_idx.values)

    # iterate over each row in the CSV
    for _, row in df.iterrows():
        lat, lon, depth = row['Latitude'], row['Longitude'], row['Depth']

        # find the central index in the NetCDF
        lat_idx, lon_idx = find_index(lat, lon)

        # extract the 9x9 neighborhood around the central point
        vicinato = bathy[lat_idx-4:lat_idx+5, lon_idx-4:lon_idx+5]

        # find the maximum value in the neighborhood
        try:
            max_bathy = np.nanmax(vicinato)  # Ignore NaN values
        except:
            continue

        # determine if max bathymetry value is greater than the CSV depth
        if (max_bathy > depth) and (max_bathy - depth > config["Input"]["depthTolerance"]):

            max_pos = np.unravel_index(np.nanargmax(vicinato), vicinato.shape)
            max_lat = latitudes[lat_idx - 4 + max_pos[0]].values
            max_lon = longitudes[lon_idx - 4 + max_pos[1]].values

            # append row with the updated depth information
            results.append([max_lat, max_lon, max_bathy])
            
        else:
            
            # append row without modification to depth
            results.append([lat, lon, depth])

    # close the NetCDF dataset
    dataset.close()

    # create a DataFrame and write the new CSV file
    output_file = os.path.join(config["Output"]["baseFolder"], "updated_thalweg.csv")
    new_df = pd.DataFrame(results, columns=["Latitude", "Longitude", "Depth"])    
    new_df.to_csv(output_file, index=False)

    # debug print
    logging.info("Thalweg improved through postprocessing")
