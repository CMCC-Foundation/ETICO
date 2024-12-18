import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
import configparser
import sys
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

def trace_transects(nc_file, point_pairs, csv_file, var_name="bathy"):
    """
    Trace transects between pairs of points and print all non-NaN points.

    Parameters:
        nc_file (str): Path to the NetCDF file.
        point_pairs (list of tuples): List of pairs of points ((lat1, lon1), (lat2, lon2)).
        csv_file (str): Path to the CSV file containing Latitude, Longitude, Depth, Direction.
        var_name (str): Name of the bathymetry variable in the NetCDF file.

    Returns:
        tuple: A tuple containing real_max and thal_max lists.
    """
    real_max = []
    thal_max = []

    # Open the NetCDF file
    dataset = nc.Dataset(nc_file, "r")

    # Extract latitude, longitude, and bathymetry variable
    lats = dataset.variables['lat'][:]
    lons = dataset.variables['lon'][:]
    bathy = dataset.variables[var_name][:]

    # Ensure bathy is a masked array if it contains NaNs
    if not np.ma.is_masked(bathy):
        bathy = np.ma.masked_invalid(bathy)

    # Load the CSV file
    csv_data = pd.read_csv(csv_file)

    # Loop through each pair of points
    for (lat1, lon1), (lat2, lon2) in point_pairs:
        print(f"========= Transect {lat1}, {lon1} -- {lat2}, {lon2} =========")

        # Create a linearly spaced set of points between the start and end points
        num_points = max(int(np.hypot(lat2 - lat1, lon2 - lon2) * 100), 100)
        lat_line = np.linspace(lat1, lat2, num_points)
        lon_line = np.linspace(lon1, lon2, num_points)

        # Interpolate bathymetry values along the line
        transect_points = np.array([lat_line, lon_line]).T

        # Extract NetCDF points along the transect
        max_depth = -np.inf
        netcdf_points = []
        for lat, lon in transect_points:
            lat_idx = (np.abs(lats - lat)).argmin()
            lon_idx = (np.abs(lons - lon)).argmin()
            value = bathy[lat_idx, lon_idx]
            if not np.isnan(value):
                netcdf_points.append((lats[lat_idx], lons[lon_idx], value))
                if value > max_depth:
                    max_depth = value

        real_max.append(max_depth)
        print(f" * Maximum depth in this transect: {max_depth}")

        # Find the closest point in the CSV file to the transect
        closest_point = None
        closest_distance = float("inf")

        for _, row in csv_data.iterrows():
            lat, lon, depth, direction = row["Latitude"], row["Longitude"], row["Depth"], row["Direction"]
            distances = np.sqrt((lat_line - lat) ** 2 + (lon_line - lon) ** 2)
            min_distance = np.min(distances)

            if min_distance < closest_distance:
                closest_distance = min_distance
                closest_point = (lat, lon, depth, direction)

        if closest_point:
            thal_depth = closest_point[2]
            thal_max.append(thal_depth)
            print(f" * Depth on the thalweg on this transect: {thal_depth}")

        print("\n")

    print(real_max)
    print(thal_max)

    dataset.close()
    return real_max, thal_max

def plot_bathymetry_with_transects(nc_file, point_pairs, var_name="bathy"):
    """
    Plot the bathymetry and overlay the transects.

    Parameters:
        nc_file (str): Path to the NetCDF file.
        point_pairs (list of tuples): List of pairs of points ((lat1, lon1), (lat2, lon2)).
        var_name (str): Name of the bathymetry variable in the NetCDF file.
    """
    # Open the NetCDF file
    dataset = nc.Dataset(nc_file, "r")

    # Extract latitude, longitude, and bathymetry variable
    lats = dataset.variables['lat'][:]
    lons = dataset.variables['lon'][:]
    bathy = dataset.variables[var_name][:]

    # Plot the bathymetry
    plt.figure(figsize=(10, 8))
    plt.contourf(lons, lats, bathy, cmap="viridis")
    plt.colorbar(label="Bathymetry")
    plt.title("Bathymetry with Transects")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # Plot the transects
    for (lat1, lon1), (lat2, lon2) in point_pairs:
        plt.plot([lon1, lon2], [lat1, lat2], color="red", marker="o", label="Transect")

    plt.legend()
    plt.show()

def plot_results(real_max, thal_max):
    """
    Plot the results and calculate RMSE, R2, and MAE.

    Parameters:
        real_max (list): Maximum depths from NetCDF.
        thal_max (list): Depths on the thalweg from the CSV file.
    """
    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(real_max, thal_max))
    r2 = r2_score(real_max, thal_max)
    mae = mean_absolute_error(real_max, thal_max)

    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")
    print(f"MAE: {mae:.4f}")

    # Plot the results
    plt.figure(figsize=(10, 6))
    indices = range(len(real_max))
    plt.plot(indices, real_max, label="Maximum Depths from NetCDF", marker="o")
    plt.plot(indices, thal_max, label="Depths from Thalweg (CSV)", marker="x")
    plt.title("Comparison of Maximum Depths by Index")
    plt.xlabel("Index")
    plt.ylabel("Depth")
    plt.xticks(indices)
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    # Ensure the configuration file and CSV file are provided as arguments
    if len(sys.argv) < 3:
        print("Usage: python script.py <config_file> <csv_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    csv_file = sys.argv[2]

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    # Get the input file name
    nc_file = config["Input"]["inputFile"]

    # Read the transects from the configuration file
    transects_raw = config["Validation"]["transects"]
    point_pairs = eval(transects_raw)  # Use eval to parse the string as a Python list

    # Call the function to trace transects
    real_max, thal_max = trace_transects(nc_file, point_pairs, csv_file)

    # Plot the bathymetry with transects
    plot_bathymetry_with_transects(nc_file, point_pairs)

    # Plot results and calculate metrics
    plot_results(real_max, thal_max)



# import numpy as np
# import netCDF4 as nc
# import matplotlib.pyplot as plt
# from scipy.interpolate import RegularGridInterpolator
# import configparser
# import sys
# import pandas as pd
# from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# def trace_transects(nc_file, point_pairs, csv_file, var_name="bathy"):
#     """
#     Trace transects between pairs of points and print all non-NaN points.

#     Parameters:
#         nc_file (str): Path to the NetCDF file.
#         point_pairs (list of tuples): List of pairs of points ((lat1, lon1), (lat2, lon2)).
#         csv_file (str): Path to the CSV file containing Latitude, Longitude, Depth, Direction.
#         var_name (str): Name of the bathymetry variable in the NetCDF file.

#     Returns:
#         tuple: A tuple containing real_max and thal_max lists.
#     """
#     real_max = []
#     thal_max = []

#     # Open the NetCDF file
#     dataset = nc.Dataset(nc_file, "r")

#     # Extract latitude, longitude, and bathymetry variable
#     lats = dataset.variables['lat'][:]
#     lons = dataset.variables['lon'][:]
#     bathy = dataset.variables[var_name][:]

#     # Ensure bathy is a masked array if it contains NaNs
#     if not np.ma.is_masked(bathy):
#         bathy = np.ma.masked_invalid(bathy)

#     # Load the CSV file
#     csv_data = pd.read_csv(csv_file)

#     # Loop through each pair of points
#     for (lat1, lon1), (lat2, lon2) in point_pairs:
#         print(f"========= Transect {lat1}, {lon1} -- {lat2}, {lon2} =========")

#         # Create a linearly spaced set of points between the start and end points
#         num_points = max(int(np.hypot(lat2 - lat1, lon2 - lon2) * 100), 100)
#         lat_line = np.linspace(lat1, lat2, num_points)
#         lon_line = np.linspace(lon1, lon2, num_points)

#         # Interpolate bathymetry values along the line
#         transect_points = np.array([lat_line, lon_line]).T

#         # Extract NetCDF points along the transect
#         max_depth = -np.inf
#         netcdf_points = []
#         for lat, lon in transect_points:
#             lat_idx = (np.abs(lats - lat)).argmin()
#             lon_idx = (np.abs(lons - lon)).argmin()
#             value = bathy[lat_idx, lon_idx]
#             if not np.isnan(value):
#                 netcdf_points.append((lats[lat_idx], lons[lon_idx], value))
#                 if value > max_depth:
#                     max_depth = value

#         real_max.append(max_depth)
#         print(f" * Maximum depth in this transect: {max_depth}")

#         # Find the closest point in the CSV file to the transect
#         closest_point = None
#         closest_distance = float("inf")

#         for _, row in csv_data.iterrows():
#             lat, lon, depth, direction = row["Latitude"], row["Longitude"], row["Depth"], row["Direction"]
#             distances = np.sqrt((lat_line - lat) ** 2 + (lon_line - lon) ** 2)
#             min_distance = np.min(distances)

#             if min_distance < closest_distance:
#                 closest_distance = min_distance
#                 closest_point = (lat, lon, depth, direction)

#         if closest_point:
#             thal_depth = closest_point[2]
#             thal_max.append(thal_depth)
#             print(f" * Depth on the thalweg on this transect: {thal_depth}")

#         print("\n")

#     dataset.close()
#     return real_max, thal_max

# def plot_bathymetry_with_transects(nc_file, point_pairs, var_name="bathy"):
#     """
#     Plot the bathymetry and overlay the transects.

#     Parameters:
#         nc_file (str): Path to the NetCDF file.
#         point_pairs (list of tuples): List of pairs of points ((lat1, lon1), (lat2, lon2)).
#         var_name (str): Name of the bathymetry variable in the NetCDF file.
#     """
#     # Open the NetCDF file
#     dataset = nc.Dataset(nc_file, "r")

#     # Extract latitude, longitude, and bathymetry variable
#     lats = dataset.variables['lat'][:]
#     lons = dataset.variables['lon'][:]
#     bathy = dataset.variables[var_name][:]

#     # Plot the bathymetry
#     plt.figure(figsize=(10, 8))
#     plt.contourf(lons, lats, bathy, cmap="viridis")
#     plt.colorbar(label="Bathymetry")
#     plt.title("Bathymetry with Transects")
#     plt.xlabel("Longitude")
#     plt.ylabel("Latitude")

#     # Plot the transects
#     for (lat1, lon1), (lat2, lon2) in point_pairs:
#         plt.plot([lon1, lon2], [lat1, lat2], color="red", marker="o", label="Transect")

#     plt.legend()
#     plt.show()

    
# def plot_results(real_max, thal_max):
#     """
#     Plot the results and calculate RMSE, R2, and MAE.

#     Parameters:
#         real_max (list): Maximum depths from NetCDF.
#         thal_max (list): Depths on the thalweg from the CSV file.
#     """
#     # Calculate metrics
#     rmse = np.sqrt(mean_squared_error(real_max, thal_max))
#     r2 = r2_score(real_max, thal_max)
#     mae = mean_absolute_error(real_max, thal_max)

#     print(f"RMSE: {rmse:.4f}")
#     print(f"R2: {r2:.4f}")
#     print(f"MAE: {mae:.4f}")

#     # Plot the results
#     plt.figure(figsize=(10, 6))
#     plt.scatter(real_max, thal_max, label="Data Points", color="blue")
#     plt.plot([min(real_max), max(real_max)], [min(real_max), max(real_max)], linestyle="--", color="red", label="Ideal Fit")
#     plt.title("Comparison of Maximum Depths")
#     plt.xlabel("Maximum Depths from NetCDF")
#     plt.ylabel("Depths from Thalweg (CSV)")
#     plt.legend()
#     plt.grid()
#     plt.show()

# if __name__ == "__main__":
#     # Ensure the configuration file and CSV file are provided as arguments
#     if len(sys.argv) < 3:
#         print("Usage: python script.py <config_file> <csv_file>")
#         sys.exit(1)

#     config_file = sys.argv[1]
#     csv_file = sys.argv[2]

#     # Read the configuration file
#     config = configparser.ConfigParser()
#     config.read(config_file)

#     # Get the input file name
#     nc_file = config["Input"]["inputFile"]

#     # Read the transects from the configuration file
#     transects_raw = config["Validation"]["transects"]
#     point_pairs = eval(transects_raw)  # Use eval to parse the string as a Python list

#     # Call the function to trace transects
#     real_max, thal_max = trace_transects(nc_file, point_pairs, csv_file)

#     # Plot the bathymetry with transects
#     # plot_bathymetry_with_transects(nc_file, point_pairs)

#     # Plot results and calculate metrics
#     plot_results(real_max, thal_max)


