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

# def postproc(config):
    
#     # open the thalweg
#     csv_file = os.path.join(config["Output"]["baseFolder"], config['Output']['thalwegCsvFile'])

#     # open the netcdf
#     netcdf_file = config["Input"]["inputFile"]

#     # Carica il file CSV
#     df = pd.read_csv(csv_file)
    
#     # Carica il file NetCDF
#     dataset = xr.open_dataset(netcdf_file)
#     bathy = dataset.variables['bathy'][:]
#     latitudes = dataset.variables['lat'][:]
#     longitudes = dataset.variables['lon'][:]
    
#     # Trova gli indici per il vicinato
#     def trova_indici(lat, lon):
#         lat_idx = (np.abs(latitudes - lat)).argmin()
#         lon_idx = (np.abs(longitudes - lon)).argmin()
#         return lat_idx.values, lon_idx.values
    
#     # Itera sui punti del CSV
#     for _, row in df.iterrows():
#         lat, lon, depth = row['Latitude'], row['Longitude'], row['Depth']
        
#         # Trova l'indice centrale nel NetCDF
#         lat_idx, lon_idx = trova_indici(lat, lon)

#         # Estrai il vicinato 9x9 attorno al punto centrale
#         vicinato = bathy[lat_idx-4:lat_idx+5, lon_idx-4:lon_idx+5]
        
#         # Trova il valore massimo nel vicinato
#         max_bathy = np.nanmax(vicinato)  # Ignora i valori NaN
        
#         # Se il massimo supera la profondità del CSV, stampa le coordinate
#         if max_bathy > depth:
#             max_pos = np.unravel_index(np.nanargmax(vicinato), vicinato.shape)
#             max_lat = latitudes[lat_idx - 4 + max_pos[0]].values
#             max_lon = longitudes[lon_idx - 4 + max_pos[1]].values
#             print(f"{max_bathy} *")
            
# #            print(f"Massimo trovato a ({max_lat}, {max_lon}) con profondità {max_bathy} > {depth}")

#         else:
#             print(depth)

#     # Chiudi il file NetCDF
#     dataset.close()    



def postproc(config):
    # Open the thalweg CSV file
    csv_file = os.path.join(config["Output"]["baseFolder"], config['Output']['thalwegCsvFile'])
    # Open the NetCDF file
    netcdf_file = config["Input"]["inputFile"]

    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Load the NetCDF file
    dataset = xr.open_dataset(netcdf_file)
    bathy = dataset.variables['bathy'][:]
    latitudes = dataset.variables['lat'][:]
    longitudes = dataset.variables['lon'][:]

    # Prepare a list to store results for the new CSV
    results = []

    # Helper function to find indices for the neighborhood
    def trova_indici(lat, lon):
        lat_idx = (np.abs(latitudes - lat)).argmin()
        lon_idx = (np.abs(longitudes - lon)).argmin()
        return int(lat_idx.values), int(lon_idx.values)

    # Iterate over each row in the CSV
    for _, row in df.iterrows():
        lat, lon, depth = row['Latitude'], row['Longitude'], row['Depth']

        # Find the central index in the NetCDF
        lat_idx, lon_idx = trova_indici(lat, lon)

        # Extract the 9x9 neighborhood around the central point
        vicinato = bathy[lat_idx-4:lat_idx+5, lon_idx-4:lon_idx+5]

        # Find the maximum value in the neighborhood
        try:
            max_bathy = np.nanmax(vicinato)  # Ignore NaN values
        except:
            continue

        # Determine if max bathymetry value is greater than the CSV depth
        if max_bathy > depth:
            max_pos = np.unravel_index(np.nanargmax(vicinato), vicinato.shape)
            max_lat = latitudes[lat_idx - 4 + max_pos[0]].values
            max_lon = longitudes[lon_idx - 4 + max_pos[1]].values
            print(f"{max_bathy} *")
            # Append row with the updated depth information
            results.append([max_lat, max_lon, max_bathy])
        else:
            print(depth)
            # Append row without modification to depth
            results.append([lat, lon, depth])

    # Close the NetCDF dataset
    dataset.close()

    # Create a DataFrame and write the new CSV file
    output_file = os.path.join(config["Output"]["baseFolder"], "updated_thalweg.csv")
    new_df = pd.DataFrame(results, columns=["Latitude", "Longitude", "Depth"])    
    new_df.to_csv(output_file, index=False)

    print(f"Updated CSV file saved to {output_file}")    
