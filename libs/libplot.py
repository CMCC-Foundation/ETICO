#!/usr/bin/python

#############################################################
#
# Requirements
#
#############################################################

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from scipy.spatial import KDTree
import matplotlib.tri as mtri
import argparse
from collections import deque
import matplotlib

matplotlib.use('TkAgg')


#############################################################
#
# Plot function
#
#############################################################

def plot(lons, lats, elements, depths, path, start_idx, end_idx, config):

    """Plot function to show the thalweg over the bathymetry map"""
    
    triang = mtri.Triangulation(lons, lats, elements)    
    plt.figure(dpi=300)
    tpc = plt.tripcolor(triang, depths, cmap=config["Plot"]["colormap"], vmin=config["Plot"]["cbarmin"], vmax=config["Plot"]["cbarmax"], edgecolors='k', linewidth=0)  
    plt.colorbar(tpc, label='Total Depth (m)')
    plt.plot(lons[path], lats[path], 'r-', linewidth=1, label='Thalweg')
    plt.plot(lons[start_idx], lats[start_idx], 'go', label='Start')
    plt.plot(lons[end_idx], lats[end_idx], 'bo', label='End')
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.axis("equal")

    # set
    if config["Plot"]["closeup"]:
        plt.xlim(config["Plot"]["lonmin"], config["Plot"]["lonmax"]) 
        plt.ylim(config["Plot"]["latmin"], config["Plot"]["latmax"])
    
    plt.title("Thalweg and Bathymetry")
    plt.legend()
    plt.grid(True)

    # save the plot to png file
    if not os.path.exists(config["Output"]["plotdirectory"]):
        os.makedirs(config["Output"]["plotdirectory"])
    outfile_name = os.path.join(config["Output"]["plotdirectory"], "unstr_thalweg.png")
    plt.savefig(outfile_name)

    # show the plot
    plt.show()
