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


# set the starting point
st_lat = 44.933
st_lon = 12.159

#########################################################
#
# get_3x3_centered_on function
#
#########################################################

def get_3x3_centered_on(ds, lat_idx, lon_idx):
    """Extract a 3x3 matrix centered on the given indices."""
    return ds.bathy.isel(lat=slice(lat_idx-1, lat_idx+2), lon=slice(lon_idx-1, lon_idx+2))


#########################################################
#
# get_matrix_centered_on function
#
#########################################################

def get_matrix_centered_on(ds, lat_idx, lon_idx, size):
    """Extract a size x size matrix centered on the given indices."""
    
    # check if size is odd. Cannot be even
    if (size % 2 == 0):
        raise Exception("matrix size cannot be even!")
    halfsize = size // 2
    
    # extract a matrix with the bathymetry and the corresponding matrix of indices
    matrix = ds.bathy.isel(lat=slice(lat_idx-halfsize, lat_idx+halfsize+1), lon=slice(lon_idx-halfsize, lon_idx+halfsize+1))
    matrix_ind = [(l1, l2) for l1 in range(lat_idx-halfsize, lat_idx+halfsize+1) for l2 in range(lon_idx-halfsize, lon_idx+halfsize+1)]
    lats_ind = range(lat_idx-halfsize, lat_idx+halfsize+1)
    lons_ind = range(lon_idx-halfsize, lon_idx+halfsize+1)

    # return the matrix and two arrays (lat and lon)
    return matrix, lats_ind, lons_ind


#########################################################
#
# get_min_index function
#
#########################################################

def get_min_index(matrix):
    """Return the index of the minimum bathymetry in the matrix."""
    
    # get the minimum
    try:
        coords = np.unravel_index(np.nanargmax(matrix), matrix.shape)
    except ValueError:
        return None, None, None

    # check if nan
    if np.isnan(matrix[coords]):
        return coords, None
    
    print("[get_min_index] === Returning %s, %s" % (coords, matrix[coords].values))
    return coords, matrix[coords].values


#########################################################
#
# get_depth function
#
#########################################################

def get_depth(ds, latlon_idx):
    
    depth = float(ds.bathy.isel(lat=latlon_idx[0], lon=latlon_idx[1]).values)
    if np.isnan(depth):
        return np.nan
    else:
        return np.round(depth, 2)


#########################################################
#
# main
#
#########################################################

if __name__ == "__main__":
    
    # Read the name of the NetCDF file
    filename = sys.argv[1]
    
    # Open the NetCDF file
    print("[__main__] === Opening file %s" % filename)
    ds = xr.open_dataset(filename)
    
    # Identify the indices of the point that is closest to the given lat and lon
    lat_given = st_lat
    lon_given = st_lon
    lat_idx = abs(ds.lat - lat_given).argmin().values
    lon_idx = abs(ds.lon - lon_given).argmin().values
        
    # Create a list of visited points
    visited = []  
    
    # Initialize a thalweg and a list of the corresponding depths
    thalweg = []
    thalweg_depth = []
    
    # save the original bathy
    ods = ds.copy(deep=True)

    # Start an 'endless' loop
    iterat = 0
    while True:
        
        # debug print
        print(colored("__main__", "blue", attrs=["bold"]) + " --- ============================================================")
        print(colored("__main__", "blue", attrs=["bold"]) + " --- Iteration %s with LAT_IDX: %s and LON_IDX: %s with DEPTH %s" % (iterat, lat_idx, lon_idx, ds.bathy.isel(lat=lat_idx, lon=lon_idx).values))

        # get the depth
        depth = get_depth(ds, (lat_idx, lon_idx))
        
        # save the point in thalweg
        thalweg.append((int(lat_idx), int(lon_idx)))
        thalweg_depth.append(depth)
        
        # mark the current cell as visited
        visited.append((int(lat_idx), int(lon_idx)))
        ds.bathy.data[lat_idx, lon_idx] = -np.inf

        # extract a size x size matrix
        size = 9
        halfsize = size // 2
        matrix, lat_ind_list, lon_ind_list = get_matrix_centered_on(ds, lat_idx, lon_idx, size)
        
        # identify the zonal direction
        zd = get_zonal_direction(matrix, lon_ind_list, lat_ind_list)
        submatrix = get_3x3_submatrix(ds.bathy, lat_idx, lon_idx)

        # identify the next element based on the zonal direction
        next_value, next_coords = find_next_through_zonal_direction(submatrix, zd, lon_idx, lat_idx)
        next_el_lat_idx = lat_idx + next_coords[0]
        next_el_lon_idx = lon_idx + next_coords[1]
        next_el_depth = ds.bathy[next_el_lat_idx, next_el_lon_idx].values  
        
        # # check neighborhood
        # allNanInfVis = True
        # neighborhood = [((lati, loni), get_depth(ds, (lati, loni))) for lati in lat_ind_list for loni in lon_ind_list ]
        # for n in neighborhood:
        
        #     print("[__main__] === Checking neighbor %s" % str(n))
            
        #     # check if nan/inf (inf = already part of the thalweg)
        #     if (not np.isnan(n[1])) and (not np.isinf(n[1])):
        #         allNanInfVis = False
        #         print("Not all the elements are nan/inf. Found %s" % str(n[1]))
        #         break                
            
        # # if all nan/inf (so out of the river or already in the thalweg), the procedure ends
        # # otherwise we go on selecting the element with the minimum bathymetry
        # if allNanInfVis:
        #     print("=== END OF THALWEG GENERATION ===")
        #     break           
        
        # # Get the index of the cell with minimum bathymetry
        # (min_lat_rel, min_lon_rel), depth = get_min_index(matrix)
        # if min_lat_rel == None:
        #     print("[__main__] === END OF THALWEG GENERATION!")
        #     break
        
        # Update the current point to the one with minimum bathymetry
        lat_idx, lon_idx = next_el_lat_idx, next_el_lon_idx
        depth = get_depth(ds, (lat_idx, lon_idx))
        print(colored("__main__", "blue", attrs=["bold"]) + " --- New matrix will be centered on %s,%s with depth %s" % (lat_idx, lon_idx, depth))
        
        # increment iteration
        iterat += 1
        if iterat == 10:
            break
        
    # #######################################################################
    # #
    # # RECAP
    # #
    # #######################################################################
    
    # print("---------------------------------------")
    # print("Our thalweg is:")
    # for p in range(len(thalweg)):
    #     print("%s) - %s [%s]" % (p, thalweg[p], thalweg_depth[p]))

    # #######################################################################
    # #
    # # PLOT
    # #
    # #######################################################################
    
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
    
    # # Close the dataset
    # ds.close()  