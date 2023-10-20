#!/usr/bin/env python3

# global reqs
from termcolor import colored
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import sys
import pdb
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy import interpolate

# local requirements
from libs.matrix_utilities import *
from libs.print_utilities import *


# def plot():
    # # manipulate ods dataset for view
    # filtered_data = ods.bathy.where(ods.bathy >= 0, other=np.nan)

    # # bounding box
    # min_lat = 44.92
    # max_lat = 45
    # min_lon = 12.06
    # max_lon = 12.23
    # # min_lat = 44.9
    # # max_lat = 45.0
    # # min_lon = 12.14
    # # max_lon = 12.26
    
    # # Extract the bathy variable
    # #bathy = ds['bathy']
    # lat = ods['lat']
    # lon = ods['lon']
    
    # # Create a figure and axis with Cartopy projection
    # fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()}, dpi=1000)

    # # Plot the bathymetry variable
    # cmap = plt.get_cmap('winter')  # Choose a colormap
    # #bathy_plot = ax.pcolormesh(lon, lat, ods.bathy, shading='gouraud', cmap=cmap)
    # # bathy_plot = ax.contour(lon, lat, ods.bathy, shading='gouraud', cmap=cmap)
    # bathy_plot = ax.pcolormesh(lon, lat, filtered_data, cmap=cmap)
    # bathy_plot = ax.pcolormesh(lon, lat, ods.bathy, cmap=cmap)
    # #bathy_plot = ax.pcolor(lon, lat, ods.bathy, cmap=cmap, antialiased=True, shading='auto')
    
    # # add the thalweg points    
    # ax.plot(float(ds.lon[thalweg[0][1]]), float(ds.lat[thalweg[0][0]]), color='red', markersize=3, marker='x') 
    # for el in thalweg:
    #     ax.plot(float(ds.lon[el[1]]), float(ds.lat[el[0]]), color='red', marker='o', markersize=0.4) #, label=str(el)))    
        
    # # Add coastlines
    # ax.add_feature(cfeature.COASTLINE)
    # ax.coastlines()

    # # Add gridlines    
    # gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
    #                   linewidth=0.25, color='gray', alpha=0.5, linestyle='--')
    # # gl.xlabels_top = False
    # # gl.ylabels_left = True
    # # gl.ylabels_right = False
    # # gl.xlabel_style = {'size': 5}
    # # gl.ylabel_style = {'size': 5}
    
    # custom_x_ticks = [1.5, 3.5]  # Replace with your custom x-axis tick positions
    # custom_y_ticks = [15, 25]    # Replace with your custom y-axis tick positions

    # ax.set_xticks(np.linspace(min_lon, max_lon, num=5))
    # for t in ax.get_xticklabels():
    #     t.set_fontsize(5)  

    # ax.set_yticks(np.linspace(min_lat, max_lat, num=5))
    # for t in ax.get_yticklabels():
    #     t.set_fontsize(5)  
    
    # # ax.set_yticks(custom_y_ticks)
    
    # # Set the limits for the x-axis and y-axis to zoom to the specified area
    # ax.set_xlim(min_lon, max_lon)
    # ax.set_ylim(min_lat, max_lat)
        
    # # Set plot title and colorbar
    # plt.title('Bathymetry and Thalweg', fontsize=5)
    # cb = plt.colorbar(bathy_plot, label='Depth (m)', shrink=0.5)
    # for t in cb.ax.get_yticklabels():
    #     t.set_fontsize(5)        

    # # Show the plot
    # plt.show()

    
    
    
    
    # # # bounding box
    # # min_lat = 44.9
    # # min_lon = 12
    # # max_lat = 45
    # # max_lon = 12.3
    
    # # # Plot the bathymetry data
    # # bathymetry_data = ds.bathy.values
    
    # # # Determine where the bathy data is non-null
    # # non_null_mask = ~np.isnan(ds.bathy)
    # # # Get the indices where the bathy data is non-null
    # # non_null_indices = np.where(non_null_mask)

    # # # Find min and max lat/lon for these indices
    # # min_lat = ds.lat[non_null_indices[0].min()]
    # # max_lat = ds.lat[non_null_indices[0].max()]
    # # min_lon = ds.lon[non_null_indices[1].min()]
    # # max_lon = ds.lon[non_null_indices[1].max()]

    # # # Crop on the real area
    # # cropped = ds.sel(lat=slice(min_lat, max_lat), lon=slice(min_lon, max_lon))
    # # bathymetry_data = cropped.bathy.values
    # # lats = cropped.lat.values
    # # lons = cropped.lon.values
    # # plt.figure()
    # # plt.pcolormesh(lons, lats, bathymetry_data, shading='auto')
    # # plt.colorbar(label='Bathymetry')

    # # # add a marker for the starting point
    # # plt.scatter(float(ds.lon[thalweg[0][1]]), float(ds.lat[thalweg[0][0]]), color='red', s=31, marker='x') 

    # # # add a marker for each point of the thalweg
    # # for el in thalweg:
    # #     plt.scatter(float(ds.lon[el[1]]), float(ds.lat[el[0]]), color='red', s=0.21, marker='o')  # 's' is the marker size
    
    # # plt.ylim([44.9, 45])
    # # plt.xlim([12, 12.25])
    # # plt.show()