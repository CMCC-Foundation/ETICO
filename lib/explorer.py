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
import os
import pdb
import csv
import logging
from termcolor import colored
from collections import Counter
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
# constants
#
################################################

DIRECTIONS = {
    "N": (0, 1),
    "NE": (1, 1),
    "E": (1, 0),
    "SE": (1, -1),
    "S": (0, -1),
    "SW": (-1, -1),
    "W": (-1, 0),
    "NW": (-1, 1)
}


################################################
#
# get adjacent directions
#
################################################

def get_adjacent_directions(item, permissive=False):

    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    # Find the index of the item
    index = directions.index(item)

    # Get the previous and next items using modular arithmetic for cyclic behavior
    previous_item = directions[(index - 1) % len(directions)]
    next_item = directions[(index + 1) % len(directions)]

    # If permissive is True, include two more adjacent items
    if permissive:
        previous_item_far = directions[(index - 2) % len(directions)]
        next_item_far = directions[(index + 2) % len(directions)]
        return [previous_item_far, previous_item, next_item, next_item_far]
    
    # return
    return [previous_item, next_item]


################################################
#
# load netcdf
#
################################################

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


################################################
#
# calculate distance
#
################################################
    
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance in meters between two points specified by their latitudes and longitudes.
    This function uses the Haversine formula.
    """
    # Radius of the Earth in meters
    R = 6371000
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


################################################
#
# find_closest_index
#
################################################


def find_closest_index(ds, lat, lon):
    """
    Find the indices in the dataset corresponding to the closest latitude and longitude.
    """
    lat_idx = np.abs(ds['lat'].values - lat).argmin()
    lon_idx = np.abs(ds['lon'].values - lon).argmin()
    return lat_idx, lon_idx



################################################
#
# get direction
#
################################################

def get_allowed_directions_complex_trend(trend, permissive=False):
    """
    Determine the allowed direction based on the complex trend
    """

    # find the number of occurrences for each direction
    direction_counts = Counter(trend)
    sorted_directions = dict(sorted(direction_counts.items(), key=lambda x: x[1], reverse=True))


    # Calculate percentage and store it along with counts in an ordered dictionary
    sorted_directions_with_percentage = {
        direction: {
            'count': count,
            'percentage': (count / len(trend)) * 100
        }
        for direction, count in sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)
    }
    
    # start building a list of allowed direction by
    # putting the most frequent with a maximum score (e.g. N:9)
    # and its adjacent ones with lower score (e.g. NE: and NW:)
    allowed_directions = []
    for direction, stats in sorted_directions_with_percentage.items():
        
        # if the list is still empty, add the most frequent
        # item, no matter its percentage
        if len(allowed_directions) == 0:
            allowed_directions.append(direction)
            adj = get_adjacent_directions(direction, permissive)
            for el in adj:
                allowed_directions.append(el)

        # consider all the other occurrences after the first
        else:
            if stats["percentage"] >= 30:
                if not direction in allowed_directions:
                    allowed_directions.append(direction)
                adj = get_adjacent_directions(direction, permissive)
                for el in adj:
                    if not el in allowed_directions:
                        allowed_directions.append(el)
            else:
                break    
    
    return allowed_directions



################################################
#
# get direction
#
################################################

def get_allowed_directions_unified(trend, lastDirection, permissive=False):
    """
    Determine the allowed direction based on the complex trend
    """

    # find the number of occurrences for each direction
    direction_counts = Counter(trend)
    sorted_directions = dict(sorted(direction_counts.items(), key=lambda x: x[1], reverse=True))


    # Calculate percentage and store it along with counts in an ordered dictionary
    sorted_directions_with_percentage = {
        direction: {
            'count': count,
            'percentage': (count / len(trend)) * 100
        }
        for direction, count in sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)
    }


    # ======= Create the list of the trend-allowed directions =======

    allowed_directions = []            
    if trend:
    
        # start building a list of allowed direction by
        # putting the most frequent with a maximum score (e.g. N:9)
        # and its adjacent ones with lower score (e.g. NE: and NW:)
        for direction, stats in sorted_directions_with_percentage.items():
            
            # if the list is still empty, add the most frequent
            # item, no matter its percentage
            if len(allowed_directions) == 0:
                allowed_directions.append(direction)
                adj = get_adjacent_directions(direction, permissive)
                for el in adj:
                    allowed_directions.append(el)
    
            # consider all the other occurrences after the first
            else:
                if stats["percentage"] >= 30:
                    if not direction in allowed_directions:
                        allowed_directions.append(direction)
                    adj = get_adjacent_directions(direction, permissive)
                    for el in adj:
                        if not el in allowed_directions:
                            allowed_directions.append(el)
                else:
                    break    
                
    # ======= Create the scores based on the last direction =======

    scores = { "N": 0, "NE": 0, "E": 0, "SE": 0, "S": 0, "SW": 0, "W": 0, "NW": 0 }
    dir_last = get_adjacent_directions(lastDirection, True)
    scores[dir_last[0]] = 1
    scores[dir_last[1]] = 5
    scores[dir_last[2]] = 5
    scores[dir_last[3]] = 1
    scores[lastDirection] = 9

    # ======= Sum 10 to the score for each direction in the trend-allowed dirs =======

    for d in scores.keys():
        if d in allowed_directions:
            scores[d] += 10

    # return
    return scores




################################################
#
# get direction
#
################################################

def get_direction(current_idx, target_idx):
    """
    Determine the direction from the current index to the target index.
    """
    d_lat = target_idx[0] - current_idx[0]
    d_lon = target_idx[1] - current_idx[1]

    # if d_lat == 0 and d_lon > 0:
    #     return "E"
    # elif d_lat == 0 and d_lon < 0:
    #     return "W"
    # elif d_lat > 0 and d_lon == 0:
    #     return "S"
    # elif d_lat < 0 and d_lon == 0:
    #     return "N"
    # elif d_lat > 0 and d_lon > 0:
    #     return "SE"
    # elif d_lat > 0 and d_lon < 0:
    #     return "SW"
    # elif d_lat < 0 and d_lon > 0:
    #     return "NE"
    # elif d_lat < 0 and d_lon < 0:
    #     return "NW"
    # else:
    #     return "Unknown"
    
    if d_lat == 0 and d_lon > 0:
        return "E"
    elif d_lat == 0 and d_lon < 0:
        return "W"
    elif d_lat > 0 and d_lon == 0:
        return "N"
    elif d_lat < 0 and d_lon == 0:
        return "S"
    elif d_lat > 0 and d_lon > 0:
        return "NE"
    elif d_lat > 0 and d_lon < 0:
        return "NW"
    elif d_lat < 0 and d_lon > 0:
        return "SE"
    elif d_lat < 0 and d_lon < 0:
        return "SW"
    else:
        return "Unknown"


################################################
#
# direction similarity
#
################################################
    
def direction_similarity(direction1, direction2):
    """
    Measure the similarity between two directions.
    """

    vector1 = DIRECTIONS.get(direction1, (0, 0))
    vector2 = DIRECTIONS.get(direction2, (0, 0))
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]

    return dot_product


################################################
#
# direction distance score
#
################################################

def direction_distance_score(dir1, dir2, trend=None):
    """
    Calculate the minimal angular distance between two compass directions and assign a score inversely proportional to the distance.

    Parameters:
    - dir1: str, first direction (e.g., 'N', 'NE', 'E', etc.)
    - dir2: str, second direction

    Returns:
    - minimal_distance_steps: int, minimal number of steps between directions
    - minimal_distance_degrees: int, minimal angular distance in degrees
    - score: float, score inversely proportional to the angular distance
    """
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    direction_map = {direction: index for index, direction in enumerate(directions)}
    
    # Validate input directions
    if dir1 not in direction_map or dir2 not in direction_map:
        raise ValueError("Invalid direction. Choose from 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'.")
    
    idx1 = direction_map[dir1]
    idx2 = direction_map[dir2]
    
    # Compute absolute difference
    diff = abs(idx1 - idx2)
    
    # Since the list is cyclic, the minimal distance is the smaller between
    # the direct difference and the wrap-around difference
    minimal_steps = min(diff, len(directions) - diff)
    
    # Each step represents 45 degrees
    minimal_distance_degrees = minimal_steps * 45

    # Calculate score inversely proportional to degrees
    # Handle the case where degrees = 0 to avoid division by zero
    if minimal_distance_degrees == 0:
        score = 1.0  # Assign maximum score when directions are the same
    else:
        score = 1 / minimal_distance_degrees  # Inverse proportionality

    # check if we are in the range of 180 degrees centered on the direction
    if trend:
        if minimal_distance_degrees > 45:
            score = 0
    else:
        if minimal_distance_degrees > 90:
            score = 0        
        
    # Optional: Normalize the score to a range (e.g., 0 to 1)
    # For example, maximum possible score is when degrees = 0 (score = 1.0)
    # Minimum possible score is when degrees = 180 (score = 1/180 ≈ 0.0056)
    # If desired, you can scale the score differently
    return minimal_steps, minimal_distance_degrees, score


################################################
#
# find_most_frequent_direction
#
################################################

def find_most_frequent_direction(directions):

    """
    Determine the most frequent direction from a list of directions.
    """

    if not directions:
        return None
    counter = Counter(directions)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else None


################################################
#
# print neighborhood
#
################################################

def print_neighborhood(bathy, lat_min, lat_max, lon_min, lon_max, candidates, selected):
    """
    Print the neighborhood grid, highlighting candidates and the selected one.
    """

    rows = []
    for lat_idx in range(lat_min, lat_max):
        row = []
        for lon_idx in range(lon_min, lon_max):
            value = bathy[lat_idx, lon_idx]
            rounded_value = round(value, 3) if not np.isnan(value) else "NaN"
            formatted_value = f"{rounded_value:>8}"
            if (lat_idx, lon_idx) == selected:
                row.append(colored(f"{formatted_value}", 'green'))
            elif (lat_idx, lon_idx) in [(lat, lon) for lat, lon, _ in candidates]:

                # Check if this cell is the selected one and append an asterisk            
                if (lat_idx, lon_idx) == (selected[0], selected[1]):
                    row.append(colored(formatted_value, 'green', attrs=["bold"]))
                else:
                    row.append(colored(formatted_value, 'green'))
                               
            else:
                row.append(formatted_value)
        rows.append(" ".join(row))

    for el in rows[::-1]:
        logging.info(el)
    
    # for lat_idx in range(lat_min, lat_max):
    #     row = []
    #     for lon_idx in range(lon_min, lon_max):
    #         value = bathy[lat_idx, lon_idx]
    #         rounded_value = round(value, 3) if not np.isnan(value) else "NaN"
    #         formatted_value = f"{rounded_value:>8}"
    #         if (lat_idx, lon_idx) == selected:
    #             row.append(colored(f"**{formatted_value}**", 'green'))
    #         elif (lat_idx, lon_idx) in [(lat, lon) for lat, lon, _ in candidates]:
    #             row.append(colored(formatted_value, 'green'))
    #         else:
    #             row.append(formatted_value)
    #     logging.info(" ".join(row))

        
################################################
#
# find_highest_bathy
#
################################################

def find_highest_bathy(ds, config):

    """
    Find the highest bathy point in the neighborhood of size windowSize
    around the given start latitude and longitude. Save the path taken in a CSV file.
    """
    try:
        bathy = ds['bathy'].values
        
        # Start from the initial coordinates and find the closest grid cell indices
        current_lat_idx, current_lon_idx = find_closest_index(ds, config['Input']['startLat'], config['Input']['startLon'])
        
        # Output CSV file setup
        csv_path = os.path.join(config['Output']['baseFolder'], config['Output']['thalwegCsvFile'])
        with open(csv_path, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Latitude', 'Longitude', 'Depth', 'Direction'])
            
            # Write the starting point to the CSV without rounding
            start_depth = bathy[current_lat_idx, current_lon_idx]
            csv_writer.writerow([config['Input']['startLat'], config['Input']['startLon'], start_depth, "None"])

        # Keep track of visited cells
        visited_cells = set()
        directions_taken = []
        last_direction = config['Input']['initialDirection']

        # ====== Start main loop ======

        lastDirection = config['Input']['initialDirection']
        for i in range(config['Input']['maxIterations']):

            # ====== Get current item and see if we're close to the end point ======
            
            # Get the current latitude, longitude, and depth
            current_lat = ds['lat'].values[current_lat_idx]
            current_lon = ds['lon'].values[current_lon_idx]
            current_depth = bathy[current_lat_idx, current_lon_idx]

            logging.info("\n")
            logging.info(f"Iteration {i + 1}: Current Position {current_lat}, {current_lon}, Indices: ({current_lat_idx}, {current_lon_idx})")
            logging.info(directions_taken[-10:])
            logging.info(last_direction)            
            
            # Check if the current position is close to the endpoint
            distance_to_end = calculate_distance(current_lat, current_lon, config["Input"]["endLat"], config["Input"]["endLon"])
            if distance_to_end <= config["Input"]["endDistance"]:
                logging.info(f"Reached endpoint proximity: {distance_to_end:.2f} meters from the target point. Stopping.")
                break

            # Write the current position to the CSV without rounding
            with open(csv_path, mode='a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([current_lat, current_lon, current_depth, directions_taken[-1] if directions_taken else "None"])
                
            # Mark the current cell as visited by setting its value to NaN
            bathy[current_lat_idx, current_lon_idx] = np.nan
            visited_cells.add((current_lat_idx, current_lon_idx))

            # ====== Determine neighborhood ======
            
            # Determine the neighborhood bounds based on full window size
            half_window = config['Input']['windowSize'] // 2
            lat_min = max(0, current_lat_idx - half_window)
            lat_max = min(bathy.shape[0], current_lat_idx + half_window + 1)
            lon_min = max(0, current_lon_idx - half_window)
            lon_max = min(bathy.shape[1], current_lon_idx + half_window + 1)

            # ====== Find candidates based on depth ======
            
            # Find the highest bathy in the neighborhood, considering tolerance and direction
            highest_bathy = -np.inf
            candidates = []

            for lat_idx in range(lat_min, lat_max):
                for lon_idx in range(lon_min, lon_max):
                    if not np.isnan(bathy[lat_idx, lon_idx]):
                        if bathy[lat_idx, lon_idx] >= highest_bathy - config['Input']['depthTolerance']:
                            highest_bathy = max(highest_bathy, bathy[lat_idx, lon_idx])
                            candidates.append((lat_idx, lon_idx, bathy[lat_idx, lon_idx]))

            # Filter candidates within the tolerance range
            candidates = [(lat, lon, val) for lat, lon, val in candidates if val >= highest_bathy - config['Input']['depthTolerance']]

            if not candidates:
                logging.info("All points in the neighborhood are visited or NaN; stopping.")
                break

            # ====== Determine score of directions for this iteration ======
            
            # initialise the best candidate
            preferred_direction = config['Input']['initialDirection'] if i < config['Input']['initPhase'] else last_direction
            best_candidate = None
            best_similarity = -np.inf
            
            # debug message: print the allowed directions based on trend:            
            allowed_dirs_trend = get_allowed_directions_complex_trend(directions_taken[-10:])
            logging.info(f"Allowed directions by complex trend: {allowed_dirs_trend}")

            # debug message: print the allowed directions based on last movement (if any)
            if i > 0:
                allowed_dirs_last = get_adjacent_directions(lastDirection, True)
                allowed_dirs_last.append(lastDirection)
            else:
                allowed_dirs_last = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']             
            logging.info(f"Allowed directions by last direction: {allowed_dirs_last}")
            
            # calculate the score
            if i >= 10:
                score = get_allowed_directions_unified(directions_taken[-10:], directions_taken[-1:][0], permissive=False)
            else:
                score = get_allowed_directions_unified([], lastDirection, permissive=False)
            logging.info(f"{score}")


            # ======= Assign a score to the candidates =======

            # initialize current score
            currentScore = 0
                        
            # iterate over candidates
            good_candidates = []
            logging.info("Candidates:")            
            for lat_idx, lon_idx, val in candidates:

                # get the direction of the new candidate
                direction = get_direction((current_lat_idx, current_lon_idx), (lat_idx, lon_idx))
                                    
                # Print direction along with other details
                candidate_info = f"Lat: {float(ds['lat'][lat_idx])}, Lon: {float(ds['lon'][lon_idx])}, " \
                    f"Indices: ({lat_idx}, {lon_idx}) - " \
                    f"Depth: {np.round(val, 3)}, Direction: {direction}, Score: {score[direction]}"
                
                ### Should be updated the best candidate?
                if score[direction] > currentScore:
                    currentScore = score[direction]
                    best_candidate = (lat_idx, lon_idx, direction)
                                                                                   
                logging.info(colored(candidate_info, 'green' if (lat_idx, lon_idx) == best_candidate else None))
            
            # Log the neighborhood
            print_neighborhood(bathy, lat_min, lat_max, lon_min, lon_max, candidates, best_candidate)
                
            # for lat_idx, lon_idx, val in candidates:
            #     direction = get_direction((current_lat_idx, current_lon_idx), (lat_idx, lon_idx))
            #     similarity_to_last = direction_similarity(direction, preferred_direction)
            #     similarity_to_frequent = direction_similarity(direction, most_frequent_direction) if most_frequent_direction else 0
            #     score = similarity_to_last + similarity_to_frequent
            #     candidate_info = f"Lat: {np.round(float(ds['lat'][lat_idx]), 3)}, Lon: {np.round(float(ds['lon'][lon_idx]), 3)}, Score: {score} (Last: {similarity_to_last}, Last10: {similarity_to_frequent})"

            #     if score > best_similarity:
            #         best_similarity = score
            #         best_candidate = (lat_idx, lon_idx, direction)

                # logging.info(colored(candidate_info, 'green' if (lat_idx, lon_idx) == best_candidate else None))

            if len(candidates) == 0:
                logging.info("No suitable candidate found; stopping (1).")
                break
                
            if not best_candidate:
                logging.info("No suitable candidate found; stopping (2).")
                break

            if best_candidate:
                highest_lat_idx, highest_lon_idx, chosen_direction = best_candidate
                selected_lat = ds['lat'].values[highest_lat_idx]
                selected_lon = ds['lon'].values[highest_lon_idx]
                selected_depth = bathy[highest_lat_idx, highest_lon_idx]
                
                # Log selected cell details
                logging.info(f"Selected cell: Lat: {float(selected_lat)}, Lon: {float(selected_lon)}, "
                             f"Indices: ({highest_lat_idx}, {highest_lon_idx}), Depth: {selected_depth}")
            
            highest_lat_idx, highest_lon_idx, chosen_direction = best_candidate
            # Log and update the direction
            logging.info(f"Moving direction: {chosen_direction}")
            directions_taken.append(chosen_direction)
            last_direction = chosen_direction

            # Move to the cell with the highest bathy
            current_lat_idx = highest_lat_idx
            current_lon_idx = highest_lon_idx


            # update last direction
            lastDirection = chosen_direction
            
        # Log all directions taken
        logging.info("Directions taken during the iterations:")
        logging.info(directions_taken)

    except Exception as e:
        logging.error(f"Error during bathy analysis: {e}")
        raise
