import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

from .configParser import parse_config

def plot_bathy_with_path(netcdf_file, csv_file, output_file, config):
    """
    Plot the bathymetry map with the path from the CSV file overlaid on top.
    
    Parameters:
    - netcdf_file: Path to the NetCDF file containing the bathy variable.
    - csv_file: Path to the CSV file containing the path points.
    - output_file: Path to save the output plot image.
    - config: Configuration dictionary with plotting settings.
    """
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
        plt.figure(figsize=(10, 8))

        # Plot the bathy data as a background
        plt.imshow(bathy, origin='lower', extent=[lons.min(), lons.max(), lats.min(), lats.max()],
                   cmap='viridis', aspect='auto')
        plt.colorbar(label="Depth")

        # Overlay the path points
        dot_size = config['Output']['dotSize']
        plt.plot(path_lons, path_lats, marker='o', color='red', markersize=dot_size, linestyle='-', linewidth=0.2, label="Path")

        # Labels and title
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Bathymetry Map with Path")
        plt.legend()

        # Save the plot to an image file
        plt.savefig(output_file, dpi=300)
        plt.close()

        print(f"Plot saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: python plot.py <netcdf_file> <csv_file> <config_file>")
    else:
        netcdf_file = sys.argv[1]
        csv_file = sys.argv[2]
        config_file = sys.argv[3]

        # Parse the configuration file
        config = parse_config(config_file)

        # Use the output directory from the config
        output_directory = config['Output']['baseFolder']
        output_file = f"{output_directory}/thalweg.png"

        # Generate the plot
        plot_bathy_with_path(netcdf_file, csv_file, output_file, config)
