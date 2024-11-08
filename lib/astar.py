#!/usr/bin/python3

################################################
#
# requirements
#
################################################

# global requirements
import numpy as np
import xarray as xr
import configparser
import sys
import heapq
import matplotlib.pyplot as plt
import pandas as pd
import logging
import os


################################################
#
# heuristic
#
################################################

def heuristic(a, b):
    """Calculate the Manhattan distance heuristic between points a and b."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


################################################
#
# a_star_search
#
################################################

def a_star_search(bathy, start, end):
    """Perform A* search from start to end on the bathymetry data, avoiding NaN cells."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        # Check neighbors
        neighbors = [(current[0] + r, current[1] + c) for r, c in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        for neighbor in neighbors:
            row, col = neighbor
            if (0 <= row < bathy.shape[0] and 0 <= col < bathy.shape[1]
                    and not np.isnan(bathy[row, col])):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []  # No path found


################################################
#
# create_path
#
################################################

def create_path(ds, start, end):
    """
    Create a connected path from start to end avoiding NaN values, setting path points to 1.

    Parameters:
    - ds: xarray Dataset containing bathymetry data with 'lat' and 'lon' coordinates.
    - start: Tuple (lat, lon) of the starting point of the river.
    - end: Tuple (lat, lon) of the ending point of the river.

    Returns:
    - Modified xarray Dataset with the path connecting start to end.
    - List of (lat, lon) tuples representing the path.
    """
    bathy = ds['bathy'].values
    latitudes = ds['lat'].values
    longitudes = ds['lon'].values

    # Convert start and end coordinates to indices
    start_idx = (np.abs(latitudes - start[0])).argmin(), (np.abs(longitudes - start[1])).argmin()
    end_idx = (np.abs(latitudes - end[0])).argmin(), (np.abs(longitudes - end[1])).argmin()

    # Perform A* search to find path
    path_indices = a_star_search(bathy, start_idx, end_idx)

    if not path_indices:
        logging.info("Error: No valid path found from start to end.")
        return ds, []

    # Update bathymetry to show the path
    bathy_with_path = np.full_like(bathy, np.nan)
    path_coords = []
    for (row, col) in path_indices:
        bathy_with_path[row, col] = 1  # Set path points to 1
        path_coords.append((latitudes[row], longitudes[col]))

    # Replace the bathymetry in the dataset with the path
    ds_with_path = ds.copy()
    ds_with_path['bathy'].values = bathy_with_path

    return ds_with_path, path_coords


################################################
#
# plot_path
#
################################################

def plot_path(ds_with_path, output_png_path, config):
    """Plot the bathymetry with the generated path."""
    logging.info("Plotting the results...")
    plt.figure(figsize=(8, 6), dpi=300)
    ds_with_path['bathy'].plot(cmap="Greys", add_colorbar=False)    
    plt.title(f"Greedy path on {config['Input']['name']}")
    plt.xlabel("Longitude (degE)")  # Add x-axis label
    plt.ylabel("Latitude (degN)")   # Add y-axis label
    plt.savefig(output_png_path)
    logging.info("Plotting completed.")


################################################
#
# start_a_star
#
################################################
    
def start_a_star(config):

    # read configuration values
    nc_path = config['Input']['inputFile']
    start = (float(config['Input']['startLat']), float(config['Input']['startLon']))
    end = (float(config['Input']['endLat']), float(config['Input']['endLon']))

    # read output file names
    output_nc_path = os.path.join(config["Output"]["baseFolder"], config["Output"]["simplifiedNcFile"])
    output_csv_path = os.path.join(config["Output"]["baseFolder"], config["Output"]["simplifiedCsvFile"])
    output_png_path = os.path.join(config["Output"]["baseFolder"], config["Output"]["simplifiedPngFile"])

    # load the input netcdf
    logging.info(f"Loading NetCDF file: {nc_path}")
    ds = xr.open_dataset(nc_path, engine="netcdf4")
    logging.info("NetCDF file loaded successfully.")

    # create the connected path
    logging.info(f"Creating path from {start} to {end}...")
    ds_with_path, path_coords = create_path(ds, start, end)

    if not path_coords:
        logging.info("Error: No path created. Check input data or path conditions.")
        return

    # save modified bathymetry with path
    logging.info(f"Saving bathymetry with path to: {output_nc_path}")
    ds_with_path.to_netcdf(output_nc_path)
    ds.close()
    ds_with_path.close()

    # save path coordinates to CSV
    logging.info(f"Saving path coordinates to CSV: {output_csv_path}")
    path_df = pd.DataFrame(path_coords, columns=["Latitude", "Longitude"])
    path_df.to_csv(output_csv_path, index=False)

    # Plot the results
    plot_path(ds_with_path, output_png_path, config)

    logging.info("Process completed.")
