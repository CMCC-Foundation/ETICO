import xarray as xr
import numpy as np
import logging
import os
import csv
from termcolor import colored
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DIRECTIONS = {
    "N": (0, -1),
    "NE": (1, -1),
    "E": (1, 0),
    "SE": (1, 1),
    "S": (0, 1),
    "SW": (-1, 1),
    "W": (-1, 0),
    "NW": (-1, -1)
}

def load_netcdf(file_path):
    """
    Load the NetCDF file and return the dataset.
    """
    try:
        ds = xr.open_dataset(file_path)
        if 'bathy' not in ds.variables:
            raise ValueError("The NetCDF file does not contain a 'bathy' variable.")
        return ds
    except Exception as e:
        logging.error(f"Failed to load NetCDF file: {e}")
        raise

def find_closest_index(ds, lat, lon):
    """
    Find the indices in the dataset corresponding to the closest latitude and longitude.
    """
    lat_idx = np.abs(ds['lat'].values - lat).argmin()
    lon_idx = np.abs(ds['lon'].values - lon).argmin()
    return lat_idx, lon_idx

def get_direction(current_idx, target_idx):
    """
    Determine the direction from the current index to the target index.
    """
    d_lat = target_idx[0] - current_idx[0]
    d_lon = target_idx[1] - current_idx[1]

    if d_lat == 0 and d_lon > 0:
        return "E"
    elif d_lat == 0 and d_lon < 0:
        return "W"
    elif d_lat > 0 and d_lon == 0:
        return "S"
    elif d_lat < 0 and d_lon == 0:
        return "N"
    elif d_lat > 0 and d_lon > 0:
        return "SE"
    elif d_lat > 0 and d_lon < 0:
        return "SW"
    elif d_lat < 0 and d_lon > 0:
        return "NE"
    elif d_lat < 0 and d_lon < 0:
        return "NW"
    else:
        return "Unknown"

def direction_similarity(direction1, direction2):
    """
    Measure the similarity between two directions.
    """
    vector1 = DIRECTIONS.get(direction1, (0, 0))
    vector2 = DIRECTIONS.get(direction2, (0, 0))
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    return dot_product

def find_most_frequent_direction(directions):
    """
    Determine the most frequent direction from a list of directions.
    """
    if not directions:
        return None
    counter = Counter(directions)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else None


def find_highest_bathy(ds, start_lat, start_lon, window_size, max_iterations, depth_tolerance, init_phase, start_direction, output_directory):
    """
    Find the highest bathy point in the neighborhood of size windowSize
    around the given start latitude and longitude. Save the path taken in a CSV file.
    """
    try:
        bathy = ds['bathy'].values
        
        # Start from the initial coordinates and find the closest grid cell indices
        current_lat_idx, current_lon_idx = find_closest_index(ds, start_lat, start_lon)
        
        # Output CSV file setup
        csv_path = os.path.join(output_directory, "path.csv")
        with open(csv_path, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Latitude', 'Longitude', 'Depth', 'Direction'])
            
            # Write the starting point to the CSV
            start_depth = round(bathy[current_lat_idx, current_lon_idx], 3)
            csv_writer.writerow([start_lat, start_lon, start_depth, "None"])

        # Keep track of visited cells
        visited_cells = set()
        directions_taken = []
        last_direction = start_direction

        for i in range(max_iterations):
            logging.info("\n")
            logging.info(f"Iteration {i + 1}: Current Position - Lat Index: {current_lat_idx}, Lon Index: {current_lon_idx}")

            # Get the current latitude, longitude, and depth
            current_lat = round(ds['lat'].values[current_lat_idx], 3)
            current_lon = round(ds['lon'].values[current_lon_idx], 3)
            current_depth = round(bathy[current_lat_idx, current_lon_idx], 3)

            # Write the current position to the CSV
            with open(csv_path, mode='a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([ds['lat'].values[current_lat_idx], ds['lon'].values[current_lon_idx], current_depth, directions_taken[-1] if directions_taken else "None"])

            # Mark the current cell as visited by setting its value to NaN
            bathy[current_lat_idx, current_lon_idx] = np.nan
            visited_cells.add((current_lat_idx, current_lon_idx))

            # Determine the neighborhood bounds based on full window size
            half_window = window_size // 2
            lat_min = max(0, current_lat_idx - half_window)
            lat_max = min(bathy.shape[0], current_lat_idx + half_window + 1)
            lon_min = max(0, current_lon_idx - half_window)
            lon_max = min(bathy.shape[1], current_lon_idx + half_window + 1)

            # Find the highest bathy in the neighborhood, considering tolerance and direction
            highest_bathy = -np.inf
            candidates = []

            for lat_idx in range(lat_min, lat_max):
                for lon_idx in range(lon_min, lon_max):
                    if not np.isnan(bathy[lat_idx, lon_idx]):
                        if bathy[lat_idx, lon_idx] >= highest_bathy - depth_tolerance:
                            highest_bathy = max(highest_bathy, bathy[lat_idx, lon_idx])
                            candidates.append((lat_idx, lon_idx, bathy[lat_idx, lon_idx]))

            # Filter candidates within the tolerance range
            candidates = [(lat, lon, val) for lat, lon, val in candidates if val >= highest_bathy - depth_tolerance]

            # Log the neighborhood and candidates
            logging.info(f"Neighborhood (Iteration {i + 1}):")
            for lat_idx in range(lat_min, lat_max):
                row = []
                for lon_idx in range(lon_min, lon_max):
                    value = bathy[lat_idx, lon_idx]
                    rounded_value = round(value, 3) if not np.isnan(value) else "NaN"
                    formatted_value = f"{rounded_value:>8}"
                    if (lat_idx, lon_idx) in [(lat, lon) for lat, lon, _ in candidates]:
                        row.append(colored(formatted_value, 'green'))
                    else:
                        row.append(formatted_value)
                logging.info(" ".join(row))

            # Determine most frequent direction from last 10 movements
            most_frequent_direction = find_most_frequent_direction(directions_taken[-10:])
            movements_display = []
            for direction in directions_taken[-10:]:
                movements_display.append(colored(direction, 'green') if direction == most_frequent_direction else direction)
            logging.info("Last 10 movements: " + " ".join(movements_display))

            # Log and select candidates
            logging.info("Candidates:")
            best_candidate = None
            best_similarity = -np.inf
            for lat_idx, lon_idx, val in candidates:
                direction = get_direction((current_lat_idx, current_lon_idx), (lat_idx, lon_idx))
                similarity_last, similarity_most_frequent, score = 0, 0, 0

                if i >= init_phase:
                    similarity_last = direction_similarity(direction, last_direction)
                    similarity_most_frequent = direction_similarity(direction, most_frequent_direction) if most_frequent_direction else 0
                    score = similarity_last + similarity_most_frequent

                lat = round(ds['lat'].values[lat_idx], 3)
                lon = round(ds['lon'].values[lon_idx], 3)
                candidate_info = f"Lat: {lat}, Lon: {lon}, Depth: {round(val, 3)}, Direction: {direction}, " \
                                 f"Score: {score} (Similarity to last: {similarity_last}, Similarity to most frequent: {similarity_most_frequent})"

                if score > best_similarity:
                    best_similarity = score
                    best_candidate = (lat_idx, lon_idx, direction, candidate_info)

                logging.info(candidate_info)

            if not candidates:
                logging.info("No candidates; stopping.")
                break

            if best_candidate:
                logging.info(colored(best_candidate[3], 'green'))
                highest_lat_idx, highest_lon_idx, chosen_direction = best_candidate[:3]
                directions_taken.append(chosen_direction)
                last_direction = chosen_direction
                current_lat_idx, current_lon_idx = highest_lat_idx, highest_lon_idx

        logging.info("Final directions:")
        logging.info(directions_taken)

    except Exception as e:
        logging.error(f"Error during bathy analysis: {e}")
        raise
