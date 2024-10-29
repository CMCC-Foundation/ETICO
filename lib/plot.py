#!/usr/bin/python3

################################################
#
# Requirements
#
################################################

# global requirements
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np
import logging
import sys
import os

# local requirements
from .configParser import parse_config


################################################
#
# logger configuration
#
################################################        

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


################################################
#
# plot_bathy_with_path
#
################################################

def plot_bathy_with_path(config):
    """
    Plot the bathymetry map with the path from the CSV file overlaid on top.
    
    Parameters:
    - netcdf_file: Path to the NetCDF file containing the bathy variable.
    - csv_file: Path to the CSV file containing the path points.
    - output_file: Path to save the output plot image.
    - config: Configuration dictionary with plotting settings.
    """

    netcdf_file = config["Input"]["inputFile"]
    csv_file = os.path.join(config["Output"]["baseFolder"], config['Output']['thalwegCsvFile'])
    output_file = os.path.join(config["Output"]["baseFolder"], config['Output']['thalwegPngFile'])
    
    try:
        
        # Load bathy data from NetCDF file
        ds = xr.open_dataset(netcdf_file)
        if 'bathy' not in ds:
            raise ValueError("The NetCDF file does not contain a 'bathy' variable.")

        bathy = ds['bathy']
        lats = ds['lat'].values
        lons = ds['lon'].values

        # Load path data from CSV file
        path_data = pd.read_csv(csv_file)

        # Extract the latitudes and longitudes from the path
        path_lats = path_data['Latitude'].values
        path_lons = path_data['Longitude'].values

        # Create the bathymetry plot
        plt.figure()
        fig, ax = plt.subplots(figsize=(10, 8), dpi=600)

        # Plot the bathy data as a background
        plt.imshow(bathy, origin='lower', extent=[lons.min(), lons.max(), lats.min(), lats.max()],
                   cmap='viridis', aspect='auto')
        plt.colorbar(label="Depth")

        # Overlay the path points if plotDots is enabled
        if config['Output'].get('plotDots', True):

            dot_size = config['Plot']['dotSize']
            dots_interval = config['Plot']['dotsInterval']

            # Plot the dots on the path and add index numbers
            plt.plot(path_lons, path_lats, marker='none', color='red', markersize=dot_size, linestyle='-', linewidth=0.2, label="Thalweg")

            # Use the dots interval to filter the path points
            path_lats = path_lats[::dots_interval]
            path_lons = path_lons[::dots_interval]
            
            # Plot the dots on the path and add index numbers
            plt.plot(path_lons, path_lats, marker='o', color='red', markersize=dot_size, linestyle='none', linewidth=0.2)
            
            # Add numbers next to the dots
            for idx, (lat, lon) in enumerate(zip(path_lats, path_lons)):
                plt.text(lon, lat, str(idx * config["Plot"]["dotsInterval"]), fontsize=config["Plot"]["dotsFontSize"], ha='right', va='bottom', color=config["Plot"]["dotsFontColour"])

        # add a marker for start and end points
        plt.plot(config["Input"]["startLon"], config["Input"]["startLat"], marker=config["Plot"]["startPointMarker"], color=config["Plot"]["startPointColour"], markersize=config["Plot"]["startPointSize"])
        plt.plot(config["Input"]["endLon"], config["Input"]["endLat"], marker=config["Plot"]["endPointMarker"], color=config["Plot"]["endPointColour"], markersize=config["Plot"]["endPointSize"])
            
        # Labels and title
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Bathymetry Map with Path")
        plt.legend()

        ax.set_aspect('equal', adjustable='box')

        
        # Save the plot to an image file
        plt.savefig(output_file, dpi=600)
        plt.close()

        logging.info(f"Plot saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")


################################################
#
# Main
#
################################################

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python plot.py <config_file>")
    else:
        config_file = sys.argv[1]

        # Parse the configuration file
        config = parse_config(config_file)

        # Generate the plot
        plot_bathy_with_path(config)
