#!/usr/bin/env python3

# global reqs
from termcolor import colored
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os
import sys
import pdb
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy import interpolate

# local requirements
from libs.matrix_utilities import *
from libs.print_utilities import *

    
#########################################################
#
# plot baseline
#
#########################################################

def plot_baseline(baseline, ds, configDict):
    
    """A function to plot the baseline on a file
    
    Parameters
    ----------
    baseline: xarray.core.dataarray.DataArray
        the original dataset
    ds: xarray.core.dataarray.DataArray
        the original dataset
    configDict: dict
        a dictionary holding the whole configuration
        
    Returns
    -------
    Nothing
    
    """

    # debug print
    print(colored("libs::plot_utilities::plot_baseline", "blue", attrs=["bold"]) + " --- Plot starting...")

    # Extract the bathy variable
    lat = ds['lat']
    lon = ds['lon']
    
    # Create a figure and axis with Cartopy projection
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()}, dpi=1000)

    # Plot the bathymetry variable
    cmap = plt.get_cmap('winter')
    
    # bathy_plot = ax.pcolormesh(lon, lat, manip_mask, cmap=cmap)
    bathy_plot = ax.pcolormesh(lon, lat, baseline, cmap=cmap)
    
    # Add gridlines    
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                      linewidth=0.25, color='gray', alpha=0.5, linestyle='--')

    # Add ticks for longitude
    ax.set_xticks(np.linspace(lon.min(), lon.max(), num=5))
    for t in ax.get_xticklabels():
        t.set_fontsize(5)  

    # Add the ticks for latitude
    ax.set_yticks(np.linspace(lat.min(), lat.max(), num=5))
    for t in ax.get_yticklabels():
        t.set_fontsize(5)  
    
    # Set plot title and colorbar
    plt.title('Baseline', fontsize=5)
    
    # Save the plot to file
    outputFile = os.path.join(configDict["plotDirectory"], configDict["baselinePlotName"])
    print(colored("libs::plot_utilities::plot_baseline", "blue", attrs=["bold"]) + " --- Saving baseline plot to %s" % outputFile)
    plt.savefig(outputFile)


#########################################################
#
# plot
#
#########################################################

def plot(ds, thalweg, thalweg_depth, configDict):
    
    """A function to plot the thalweg
    
    Parameters
    ----------
    ds: xarray.core.dataarray.DataArray
        the original dataset
    thalweg: list
        a list of [lat_idx, lon_idx] elements
    thalweg_depth: list
        a list of the depths for all the values
    configDict: dict
        a dictionary holding the whole configuration
        
    Returns
    -------
    Nothing
    
    """

    print(colored("libs::plot_utilities::plot", "blue", attrs=["bold"]) + " --- Plot starting...")

    # bounding box
    min_lat = 44.92
    max_lat = 45
    min_lon = 12.06
    max_lon = 12.23

    # Extract the bathy variable
    bathy = ds['bathy']
    lat = ds['lat']
    lon = ds['lon']
    
    # Create a figure and axis with Cartopy projection
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()}, dpi=1000)

    # Plot the bathymetry variable
    cmap = plt.get_cmap('winter')  # Choose a colormap
    bathy_plot = ax.pcolormesh(lon, lat, ds.bathy, cmap=cmap)
    
    # add the thalweg points    
    ax.plot(float(ds.lon[thalweg[0][1]]), float(ds.lat[thalweg[0][0]]), color='red', markersize=3, marker='x') 
    counter = 0
    segPointsLons = [float(ds.lon[thalweg[0][1]])]
    segPointsLats = [float(ds.lat[thalweg[0][0]])]
    for el in thalweg:
        counter += 1
        if counter % configDict["pointSparsity"] == 0:

            # draw points
            if configDict["pointsEnabled"]:            
                ax.plot(float(ds.lon[el[1]]), float(ds.lat[el[0]]), color='red', marker='.', markersize=configDict["pointsSize"])
                
            # draw labels
            if configDict["labelsEnabled"]:
                ax.text(float(ds.lon[el[1]]), float(ds.lat[el[0]]), str(counter), fontsize=configDict["labelsSize"])
            
            # draw segments
            segPointsLats.append(float(ds.lat[el[0]]))
            segPointsLons.append(float(ds.lon[el[1]]))            
            ax.plot(segPointsLons, segPointsLats, linestyle="-", linewidth=0.4, color='black')
            segPointsLats = [float(ds.lat[el[0]])]
            segPointsLons = [float(ds.lon[el[1]])]         

    # Add coastlines
    ax.add_feature(cfeature.COASTLINE)
    ax.coastlines()

    # Add gridlines    
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                      linewidth=0.25, color='gray', alpha=0.5, linestyle='--')
    # gl.xlabels_top = False
    # gl.ylabels_left = True
    # gl.ylabels_right = False
    # gl.xlabel_style = {'size': 5}
    # gl.ylabel_style = {'size': 5}
    
    # custom_x_ticks = [1.5, 3.5]  # Replace with your custom x-axis tick positions
    # custom_y_ticks = [15, 25]    # Replace with your custom y-axis tick positions

    # ax.set_xticks(np.linspace(min_lon, max_lon, num=5))
    # for t in ax.get_xticklabels():
    #     t.set_fontsize(5)  

    # ax.set_yticks(np.linspace(min_lat, max_lat, num=5))
    # for t in ax.get_yticklabels():
    #     t.set_fontsize(5)  
    
    # # ax.set_yticks(custom_y_ticks)
    
    # Set the limits for the x-axis and y-axis to zoom to the specified area
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
        
    # Set plot title and colorbar
    plt.title('Bathymetry and Thalweg', fontsize=5)
    cb = plt.colorbar(bathy_plot, label='Depth (m)', shrink=0.5)
    for t in cb.ax.get_yticklabels():
        t.set_fontsize(5)        

    # Show the plot
    plt.show()

    print(colored("libs::plot_utilities::plot", "blue", attrs=["bold"]) + " --- Generation of plot complete.")