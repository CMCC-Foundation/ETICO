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
import sys
import os
import pdb
import csv
import math
import logging
import traceback
from termcolor import colored
from collections import Counter
from tabulate import tabulate
from math import radians, cos, sin, sqrt, atan2
from scipy.spatial.distance import euclidean
from scipy.ndimage import distance_transform_edt



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
# find_row_index
#
################################################

def find_row_index(df, target_lat, target_lon):
    """
    Find the index of the row containing the specified latitude and longitude.
    
    Parameters:
        csv_file (str): Path to the CSV file with 'latitude' and 'longitude' columns.
        target_lat (float): The latitude to search for.
        target_lon (float): The longitude to search for.
    
    Returns:
        int or None: The index of the row if found, otherwise None.
    """
    
    # Find the row index where latitude and longitude match the target values
    logging.error(f"Looking for {target_lat}, {target_lon}")

    row = df[(df['Latitude'] == target_lat) & (df['Longitude'] == target_lon)]
    
    # Check if a match was found and return the index
    if not row.empty:
        return row.index[0]
    else:
        return None


################################################
#
# get_path_distance
#
################################################

def get_path_distance(bathy_ds, path_ds, path_df, start, end, current):
    """
    Calculate path distances from the 'current' point to 'start' and 'end' points.
    
    Parameters:
        bathy_ds (xarray.Dataset): Dataset containing the 'bathy' variable.
        path_ds (xarray.Dataset): Dataset containing the path from start to end.
        start (tuple): Coordinates (lat, lon) for the start point.
        end (tuple): Coordinates (lat, lon) for the end point.
        current (tuple): Coordinates (lat, lon) for the current point.
    
    Returns:
        dict: A dictionary containing path distances for 'current' to 'start' and 'end'.
    """
    
    # Define coordinates as lat/lon grids
    lat_grid = bathy_ds['lat'].values
    lon_grid = bathy_ds['lon'].values
    
    # Helper function to find the nearest grid indices for a given lat/lon point
    def find_nearest_indices(lat, lon):
        lat_idx = np.abs(lat_grid - lat).argmin()
        lon_idx = np.abs(lon_grid - lon).argmin()
        return lat_idx, lon_idx
    
    # # Get indices for start, end, and current points
    # start_idx = find_nearest_indices(*start)
    # end_idx = find_nearest_indices(*end)
    # logging.error(f"The start point is: {start}")
    # logging.error(f"Indices of start point are: {start_idx}")
    # logging.error(f"The end point is: {end}")
    # logging.error(f"Indices of end point are: {end_idx}")
    current_idx = find_nearest_indices(*current)
    # near_lat = lat_grid[current_idx[0]]
    # near_lon = lon_grid[current_idx[1]]


    # Initialize minimum distance and closest point
    min_distance = float('inf')
    closest_point = None
    closest_index = 0
    total_index = 0
    
    # Iterate over each row and calculate Euclidean distance
    for index, row in path_df.iterrows():
        
        lat, lon = row['Latitude'], row['Longitude']
        distance = np.sqrt((lat - current[0]) ** 2 + (lon - current[1]) ** 2)
        
        # Update the closest point if a smaller distance is found
        if distance < min_distance:
            min_distance = distance
            closest_point = row
            closest_index = total_index

        total_index += 1

    logging.error(f"DISTANCE FROM START: {closest_index}")
    logging.error(f"DISTANCE FROM END: {total_index - closest_index}")
    return closest_index, total_index-closest_index
    
    # logging.error(f"INDICE {find_row_index(path_df, near_lat, near_lon)}")
    # logging.error(f"{bathy_ds['bathy'][current_idx[0], current_idx[1]]}")
    # , bathy_ds['bathy'][current_idx[1]])}")
    
    # # Path Distance (following path in path_ds)
    # path_var = path_ds['bathy'].values  # Replace 'path' with actual path variable name
    
    # # Function to calculate path distance by traversing path cells
    # def traverse_path(start_idx, target_idx):
    #     distance = 0
    #     visited = set()
    #     current = start_idx
        
    #     while current != target_idx:
    #         visited.add(current)
    #         # Find neighboring cells on the path
    #         neighbors = [
    #             (current[0] + 1, current[1]), (current[0] - 1, current[1]),
    #             (current[0], current[1] + 1), (current[0], current[1] - 1)
    #         ]
    #         # Select the next cell on the path that hasn't been visited
    #         next_cell = None
    #         for n in neighbors:
    #             if n not in visited and 0 <= n[0] < path_var.shape[0] and 0 <= n[1] < path_var.shape[1] and path_var[n] == 1:
    #                 next_cell = n
    #                 break
            
    #         if not next_cell:  # If we reach a dead-end, the path is broken
    #             return None
            
    #         # Add distance (assuming a unit grid, otherwise use actual distances)
    #         distance += 1
    #         current = next_cell
        
    #     return distance
    
    # path_distance_start = traverse_path(start_idx, current_idx)
    # path_distance_end = traverse_path(current_idx, end_idx)

    path_distance_start, path_distance_end = None, None
    # return path_distance_start, path_distance_end


################################################
#
# REFACTORING === mean_angle
#
################################################

def mean_angle(angles):
    # Convert angles from degrees to radians
    angles_rad = [math.radians(angle) for angle in angles]

    # Calculate the mean sine and cosine values
    sin_sum = sum(math.sin(angle) for angle in angles_rad)
    cos_sum = sum(math.cos(angle) for angle in angles_rad)
    
    # Calculate the mean angle in radians
    mean_angle_rad = math.atan2(sin_sum, cos_sum)
    
    # Convert the mean angle back to degrees
    mean_angle_deg = math.degrees(mean_angle_rad)
    
    # Ensure the result is in the range -180 to 180
    if mean_angle_deg > 180:
        mean_angle_deg -= 360
    elif mean_angle_deg <= -180:
        mean_angle_deg += 360
    
    return mean_angle_deg


################################################
#
# REFACTORING === get_final_direction
#
################################################

def normalise(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


################################################
#
# REFACTORING === get_final_direction
#
################################################

def get_final_direction(point1, point2):

    point1_lat, point1_lon = point1
    point2_lat, point2_lon = point2

    # check west-east direction
    if point2_lon > point1_lon:
        we = "E"
    elif point2_lon < point1_lon:
        we = "W"
    else:
        we = ""

    # check west-east direction
    if point2_lat > point1_lat:
        ns = "N"
    elif point2_lat < point1_lat:
        ns = "S"
    else:
        ns = ""

    # return
    return f"{ns}{we}"


################################################
#
# REFACTORING === get_final_direction
#
################################################

def multiply_score(score):

    # logging.info(f"Starting with {score}")                    

    # definisci n intervalli nel range da 0 a 360
    N = 10
    a = 0.5        # Exponent for nonlinear mapping

    # Step 1: Generate uniformly spaced points in [0,1)
    u = np.linspace(0, 360, N, endpoint=False)
    
    # Step 2: Apply nonlinear transformation
    # intervals = 360 * (1 - np.power(u, a))
    intervals = u
    # for i in range(len(intervals)):
    #     logging.info(f"{i} --- {np.power(2, i)}")
    
    # find the multiplier
    for i in range(len(intervals)):
        try:
            # logging.error(f"STEP {i} -- checking if {intervals[i]} <= {score} < {intervals[i+1]}")
            if (score >= intervals[i]) and (score < intervals[i+1]):
                break
        except IndexError:
            pass

    oldscore = score
    score = score * (np.power(2, i))
    # logging.info(f"Stopped at {i} -- old score is {oldscore} -- multiplied {np.power(2, i)} -- new score is {score}")                    
        
    # return
    return score



################################################
#
# REFACTORING === cardinal_to_angle
#
################################################

def cardinal_to_angle(cardinal_direction):
    """
    Restituisce l'angolo corrispondente a un dato punto cardinale usando il Nord geodetico come riferimento.
    
    Parametri:
    - cardinal_direction (str): Il punto cardinale, come 'N', 'S', 'E', 'W',
                                o combinazioni come 'NE', 'NW', 'SE', 'SW'.
    
    Restituisce:
    - float: L'angolo corrispondente in gradi (N = 0°, E = 90°, S = 180°, W = 270°).
    """
    cardinal_direction = cardinal_direction.upper()
    # cardinal_to_angle_map = {
    #     'N': 0,
    #     'NE': 45,
    #     'E': 90,
    #     'SE': 135,
    #     'S': 180,
    #     'SW': 225,
    #     'W': 270,
    #     'NW': 315
    # }
    cardinal_to_angle_map = {
        'N': 0,
        'NE': 45,
        'E': 90,
        'SE': 135,
        'S': 180,
        'SW': -135,
        'W': -90,
        'NW': -45
    }

    return cardinal_to_angle_map.get(cardinal_direction, None)


################################################
#
# REFACTORING === angle_to_cardinal
#
################################################

def angle_to_cardinal(angle):
    """
    Restituisce il punto cardinale più vicino dato un angolo rispetto al Nord geodetico.
    
    Parametri:
    - angle (float): Angolo in gradi (0-360).
    
    Restituisce:
    - str: Il punto cardinale più vicino (N, NE, E, SE, S, SW, W, NW).
    """
    # Normalizza l'angolo tra 0 e 360 gradi
    angle = angle % 360

    # Mappa degli angoli per i punti cardinali principali e intermedi
    angle_to_cardinal_map = {
        (-22.5, 22.5): 'N',
        (22.5, 67.5): 'NE',
        (67.5, 112.5): 'E',
        (112.5, 157.5): 'SE',
        (157.5, 180): 'S',
        (-180, -157.5): 'S',
        (-157.5, -112.5): 'SW',
        (-112.5, -67.5): 'W',
        (-67.5, -22.5): 'NW'
    }
    
    # # Mappa degli angoli per i punti cardinali principali e intermedi
    # angle_to_cardinal_map = {
    #     (337.5, 22.5): 'N',
    #     (22.5, 67.5): 'NE',
    #     (67.5, 112.5): 'E',
    #     (112.5, 157.5): 'SE',
    #     (157.5, 202.5): 'S',
    #     (202.5, 247.5): 'SW',
    #     (247.5, 292.5): 'W',
    #     (292.5, 337.5): 'NW'
    # }

    # Trova il punto cardinale corrispondente all'angolo
    for (start, end), cardinal in angle_to_cardinal_map.items():
        if start <= angle < end:
            return cardinal

    # Caso speciale per 0 o 360 gradi (Nord geodetico)
    return 'N'


################################################
#
# REFACTORING === calculate geodetic bearing
#
################################################

def calculate_geodetic_bearing(lat1, lon1, lat2, lon2):
    """
    Calcola l'angolo tra due punti geografici rispetto al Nord geodetico.
    
    Parametri:
    - lat1, lon1: Coordinate del punto iniziale (in gradi decimali).
    - lat2, lon2: Coordinate del punto finale (in gradi decimali).
    
    Restituisce:
    - float: Angolo in gradi rispetto al Nord geodetico (0° = Nord, 90° = Est, 180° = Sud, 270° = Ovest).
    """
    # Converti le coordinate in radianti
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Calcolo della differenza longitudinale
    dlon = lon2 - lon1
    
    # Calcolo dell'azimut geodetico
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    initial_bearing = math.atan2(x, y)
    
    # Converti l'angolo da radianti a gradi e normalizza tra 0 e 360
    initial_bearing = math.degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360


    # EXPERIMENTAL 180
    # converti l'angolo in [-180, 180]
    if bearing > 180:
        bearing = -1 * (360 - bearing)
    
    return bearing


################################################
#
# REFACTORING === constants
#
################################################

def calculate_angle(previous, current, candidate, distance_previous_current=None):
    """
    Calcola l'angolo in gradi tra i segmenti previous-candidate e current-candidate.
    
    Parametri:
    - previous (tuple): (latitudine, longitudine) del punto precedente.
    - current (tuple): (latitudine, longitudine) del punto corrente.
    - candidate (tuple): (latitudine, longitudine) del punto candidato.
    - distance_previous_current (float, opzionale): distanza pre-calcolata tra previous e current.
    
    Restituisce:
    - float: angolo in gradi tra i segmenti previous-candidate e current-candidate.
    """
    # Converti latitudine e longitudine in radianti
    lat_curr, lon_curr = map(math.radians, current)
    lat_cand, lon_cand = map(math.radians, candidate)

    # Se la distanza previous-current è fornita, calcola solo candidate-current
    if distance_previous_current is None:
        if previous is None:
            raise ValueError("Il parametro 'previous' non può essere None se 'distance_previous_current' non è fornito.")
        lat_prev, lon_prev = map(math.radians, previous)
        
        # Calcolo del vettore previous-candidate
        vec_prev_cand = (
            math.cos(lat_cand) * math.cos(lon_cand) - math.cos(lat_prev) * math.cos(lon_prev),
            math.cos(lat_cand) * math.sin(lon_cand) - math.cos(lat_prev) * math.sin(lon_prev),
            math.sin(lat_cand) - math.sin(lat_prev)
        )
    else:
        # Quando la distanza è fornita, usa la distanza per scalare la direzione
        vec_prev_cand = (
            distance_previous_current * math.cos(lon_curr - lon_cand),
            distance_previous_current * math.sin(lon_curr - lon_cand),
            0
        )
    
    # Calcolo del vettore current-candidate
    vec_curr_cand = (
        math.cos(lat_cand) * math.cos(lon_cand) - math.cos(lat_curr) * math.cos(lon_curr),
        math.cos(lat_cand) * math.sin(lon_cand) - math.cos(lat_curr) * math.sin(lon_curr),
        math.sin(lat_cand) - math.sin(lat_curr)
    )
    
    # Calcolo del prodotto scalare
    dot_product = sum(a * b for a, b in zip(vec_prev_cand, vec_curr_cand))
    
    # Gestione dei casi speciali di vettori coincidenti
    if dot_product == 0:
        return 0.0  # Restituisce 0 gradi se i punti sono coincidenti o molto vicini
    
    # Calcolo dell'angolo in radianti e conversione in gradi
    angle_rad = math.acos(dot_product / (math.sqrt(sum(a ** 2 for a in vec_prev_cand)) * math.sqrt(sum(b ** 2 for b in vec_curr_cand))))
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg


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
# print neighborhood
#
################################################

def print_neighborhood(current_lat_idx, current_lon_idx, bathy, lat_min, lat_max, lon_min, lon_max, candidates, selected=None):
    
    """
    Stampa la griglia del vicinato, evidenziando i candidati e il punto selezionato.
    
    Per ogni candidato, stampa sia la profondità che l'angolo.
    """

    
    # Costruisci un dizionario dei candidati indicizzati per 'lat_idx-lon_idx'
    candict = {f"{candidate['lat_idx']}{candidate['lon_idx']}": candidate for candidate in candidates}

    # Costruisci la tabella
    rows = []
    srows = []
    trows = []
    for lat_idx in range(lat_min, lat_max):        
        row = []
        srow = ""
        trow = []

        for lon_idx in range(lon_min, lon_max):
            # Recupera il valore della profondità
            value = bathy[lat_idx, lon_idx]
            rounded_value = round(value, 3) if not np.isnan(value) else "NaN"
            
            # Recupera l'angolo, se disponibile
            key = f"{lat_idx}{lon_idx}"
            if key in candict:
                angle = np.round(candict[key]["angle"], 2)
                score = np.round(candict[key]["score"], 2)
                # Formatta profondità e angolo per la visualizzazione
                formatted_value = colored(f"{rounded_value:>8} ({score:>5.1f}°)", "green")                
            else:

                if (current_lat_idx == lat_idx) and (current_lon_idx == lon_idx):                                 
                    formatted_value = colored(f"{rounded_value:>8} ({0.0:>5.1f}°)", "red")
                else:
                    formatted_value = f"{rounded_value:>8} ({0.0:>5.1f}°)"                    

            # prepare the string
            if (current_lat_idx == lat_idx) and (current_lon_idx == lon_idx):
                cell = colored(f"X", "red")                
            else:
                if key in candict:                
                    g1_score = np.round(candict[key]["g1_score"], 2)
                    g2_score = np.round(candict[key]["g2_score"], 2)
                    g3_score = np.round(candict[key]["g3_score"], 2)
                    try:
                        if selected:
                            if (candict[key]["lon_idx"] == selected["lon_idx"]) and (candict[key]["lat_idx"] == selected["lat_idx"]):
                                cell = colored(f"{rounded_value} ({str(g1_score)}, {str(g2_score)}, {str(g3_score)})", "green")
                            else:
                                cell = f"{rounded_value} ({str(g1_score)}, {str(g2_score)}, {str(g3_score)})"                                
                        else:
                            cell = f"{rounded_value} ({str(g1_score)}, {str(g2_score)}, {str(g3_score)})"
                    except:
                        logging.error(traceback.print_exc())
                        logging.error(selected)
                        sys.exit()
                else:
                    g1_score = None
                    g2_score = None            
                    g3_score = None            
                    cell = "None"
                    
            trow.append(cell)
            srow += f"{cell}\t\t"  # Separate cells with a tab
            
        # print(f"{lat_idx} --- {srow}")
        # print("____")
                    
        row.append(formatted_value)
        rows.append(" ".join(row))
        srows.append(srow)
        trows.append(trow)

    rtrows = trows.reverse()
        
    # print the table
    table = tabulate(
        trows
    )
    logging.info(table)


################################################
#
# REFACTORING === find_highest_bathy
#
################################################

def find_highest_bathy(ds, path_ds, path_df, config, start_lat=None, start_lon=None, start_dir=None, start_counter=0, distance_from_start=0):

    """
    Find the highest bathy point in the neighborhood of size windowSize
    around the given start latitude and longitude. Save the path taken in a CSV file.
    """

    # initialise restart
    restart = False
    comebackAlert = False
    comebackCount = 0
    comebackStart = None

   
    try:
        
        bathy = ds['bathy'].values

        # ====== decide wether to restart or not ======
        
        # Start from the initial coordinates and find the closest grid cell indices
        if not start_lat:

            logging.info(colored("FIRST RUN", "red", attrs=["bold"]))
            
            # we are on a brand new start
            current_lat_idx, current_lon_idx = find_closest_index(ds, config['Input']['startLat'], config['Input']['startLon'])

            # Output CSV file setup
            csv_path = os.path.join(config['Output']['baseFolder'], config['Output']['thalwegCsvFile'])
            csvfile = open(csv_path, mode='w', newline='')
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Latitude', 'Longitude', 'Depth', 'Direction'])
                    
            # Write the starting point to the CSV without rounding
            start_depth = bathy[current_lat_idx, current_lon_idx]
            csv_writer.writerow([config['Input']['startLat'], config['Input']['startLon'], start_depth, "None"])
            
            # Keep track of visited cells
            visited_cells = set()
            history = []
            lastDirection = cardinal_to_angle(config['Input']['initialDirection'])
            
        else:

            logging.info(colored("RESTART RUN", "red", attrs=["bold"]))

            
            # calculate the distance from start and end point
            start_point = (config['Input']['startLat'], config['Input']['startLon'])
            end_point = (config['Input']['endLat'], config['Input']['endLon'])
            current = (start_lat, start_lon)
            d_from_start, d_from_end = get_path_distance(ds, path_ds, path_df, start_point, end_point, current)
            distance_from_start = d_from_start
            
            # we are on a restart condition
            current_lat_idx, current_lon_idx = find_closest_index(ds, start_lat, start_lon)

            # Output CSV file setup
            csv_path = os.path.join(config['Output']['baseFolder'], config['Output']['thalwegCsvFile'])
            csvfile = open(csv_path, mode='a', newline='')
            csv_writer = csv.writer(csvfile)

            # Keep track of visited cells
            visited_cells = set()
            history = []
            lastDirection = start_dir
            

        # ====== Start main loop ======

        # make a copy of the original bathymetry to work on that
        working_bathy = bathy.copy()
               
        for i in range(start_counter, config['Input']['maxIterations']):

            # debug message
            logging.info(f"")
            logging.info(f"")
            logging.info(f"")
            logging.info(f"========= Starting iteration {i} =========")
            
            # extract info on the current point
            current_lat = ds['lat'].values[current_lat_idx]
            current_lon = ds['lon'].values[current_lon_idx]
            current_depth = working_bathy[current_lat_idx, current_lon_idx]
            logging.info(f"We are now on {current_lat}, {current_lon} ({current_lat_idx}, {current_lon_idx}). Previous angle: {lastDirection} ({config['Input']['initialDirection']})")

            # mark the cell as visited
            visited_cells.add((current_lat_idx, current_lon_idx))
            
            # check if the current position is close to the endpoint, in case exit
            distance_to_end = calculate_distance(current_lat, current_lon, config["Input"]["endLat"], config["Input"]["endLon"])
            if distance_to_end <= config["Input"]["endDistance"]:
                logging.info(f"Reached endpoint proximity: {distance_to_end:.2f} meters from the target point. Stopping.")
                restart = False
                break

            # ====== Determine neighborhood ======

            half_window = config['Input']['windowSize'] // 2
            lat_min = max(0, current_lat_idx - half_window)
            lat_max = min(bathy.shape[0], current_lat_idx + half_window + 1)
            lon_min = max(0, current_lon_idx - half_window)
            lon_max = min(bathy.shape[1], current_lon_idx + half_window + 1)

            # ====== Analyse the neighborhood ======
            
            # Find the deepest point in the neighborhood, considering tolerance and direction
            highest_bathy = -np.inf
            candidates = []
            best_score = np.inf
            best_candy = None

            # first of all, look for the maximum bathymetry value
            for lat_idx in range(lat_min, lat_max):
                for lon_idx in range(lon_min, lon_max):
                    
                    # if the current point is not nan and is deeper than the current max, update the max!
                    if not np.isnan(working_bathy[lat_idx, lon_idx]):
                        if working_bathy[lat_idx, lon_idx] >= highest_bathy:
                            highest_bathy = working_bathy[lat_idx, lon_idx]
            logging.info(f"Maximum in neighborhood: {highest_bathy}")
            logging.info(f"Last direction: {lastDirection}")
            logging.info(f"Trend is {history[-10:]}")
            logging.info(f"Trend direction is {mean_angle(history[-10:])}")
            # logging.info(f"Trend direction is {np.mean(history[-10:])}")
                            
            # now iterate to process the candidates
            max_trend = 0
            for lat_idx in range(lat_min, lat_max):
                for lon_idx in range(lon_min, lon_max):                    

                    # skip current point
                    if (lat_idx == current_lat_idx) and (lon_idx == current_lon_idx):
                        continue
                    
                    # initialise the candidate
                    candidate = {"lat": ds['lat'].values[lat_idx], "lon": ds['lon'].values[lon_idx],
                                 "lat_idx": lat_idx, "lon_idx": lon_idx, "angle": None,
                                 "g1_score": None, "g2_score": None, "g3_score": None,
                                 "score": None, "depth": working_bathy[lat_idx, lon_idx]}

                    # if depth is nan, we can exclude this candidate
                    if np.isnan(candidate["depth"]):
                        continue
                    
                    # determine g-component depth_score
                    try:
                        depth_score = 1 / float(candidate["depth"])
                    except ZeroDivisionError:
                        depth_score = 9999
                    
                    # determine g-component "last direction"
                    bearing = calculate_geodetic_bearing(current_lat, current_lon, ds['lat'][lat_idx], ds['lon'][lon_idx])
                    angle_score = np.abs(bearing - lastDirection)

                    # determine g-component "trend direction"
                    if len(history) >= 10:
                        trend_score = np.abs(bearing - mean_angle(history[-10:]))
                        # trend_score = np.abs(bearing - np.mean(history[-10:]))
                        trend_score = multiply_score(trend_score)
                        if trend_score > max_trend:
                            max_trend = trend_score
                    else:
                        trend_score = 0
                                                        
                    # determine g
                    g = depth_score + 0.1 * angle_score + trend_score

                    candidate["g1_score"] = normalise(depth_score, 0, highest_bathy)
                    candidate["g2_score"] = normalise(angle_score, 0, 359)
                    if len(history) >= 10:
                        # candidate["g3_score"] = normalise(trend_score, 0, max_trend)
                        candidate["g3_score"] = normalise(trend_score, -180, 180)
                    else:
                        candidate["g3_score"] = 0
                    g = candidate["g1_score"] + candidate["g2_score"] + 1.3 * candidate["g3_score"]
                    
                    # update the candidate and add it to the list
                    candidate["score"] = g
                    candidate["angle"] = bearing
                    candidates.append(candidate)

                    if candidate["score"] < best_score:
                        best_score = candidate["score"]
                        best_candy = candidate
                        best_direction = bearing
                    
                    # logging.info(f"Adding: {candidate}")

            # Log the neighborhood
            try:
                if best_candy:
                    print_neighborhood(current_lat_idx, current_lon_idx, working_bathy, lat_min, lat_max, lon_min, lon_max, candidates, best_candy)
                else:
                    print_neighborhood(current_lat_idx, current_lon_idx, working_bathy, lat_min, lat_max, lon_min, lon_max, candidates, None)
            except:
                logging.error(traceback.print_exc())
                pdb.set_trace()
                    
            # did we find a candidate?
            if best_candy:

                # debug message
                # logging.info(f"SELECTED: {best_candy}")
                logging.info(f"SELECTED ==> lat: %s, lon: %s, lat_idx: %s, lon_idx: %s, g1: %s, g2: %s, g3: %s, depth: %s" % (
                    best_candy["lat"], best_candy["lon"],
                    best_candy["lat_idx"], best_candy["lon_idx"],
                    np.round(best_candy["g1_score"],3), np.round(best_candy["g2_score"],3), np.round(best_candy["g3_score"],3),
                    np.round(best_candy["depth"],3)
                ))
                final_dir = get_final_direction((current_lat, current_lon), (best_candy["lat"], best_candy["lon"]))
                logging.info(f"Moving towards {final_dir}")

                # set to null all the elements in the neighborhood before moving
                for lat_idx in range(lat_min, lat_max):
                    for lon_idx in range(lon_min, lon_max):
                        
                        # Set the bathymetry value to np.nan for the surrounding points
                        working_bathy[lat_idx, lon_idx] = np.nan                
                
                # update the index of the current element
                current_lat_idx = best_candy["lat_idx"]
                current_lon_idx = best_candy["lon_idx"]
                lastDirection = best_direction
                history.append(lastDirection)

                # update the csv
                csv_writer.writerow([best_candy['lat'], best_candy['lon'], best_candy["depth"], best_direction])


                # ========= check for comeback =========
                
                # calculate the distance from start and end point
                start_point = (config['Input']['startLat'], config['Input']['startLon'])
                end_point = (config['Input']['endLat'], config['Input']['endLon'])
                current = (best_candy["lat"], best_candy["lon"])
                d_from_start, d_from_end = get_path_distance(ds, path_ds, path_df, start_point, end_point, current)               
                
                # check if we are going close to start point (and we should not!)
                if comebackAlert: # if we are already on alert:

                    if d_from_start < distance_from_start: # the comeback goes on

                        # increment the count of consecutive points
                        comebackCount += 1

                        # have we reached the 5 comeback position?
                        if comebackCount == 5:

                            # notify the user                        
                            logging.info(f"============== COMEBACK IDENTIFIED -- Let's start again from last good position! ({comebackPosition}) ===================")
                            
                            # exit from the procedure and make it restart from the comebackStart point
                            return True, comebackPosition[0], comebackPosition[1], comebackDirection, i-5, comebackStart
                        
                        else:
                        
                            # notify the user                        
                            logging.info(f"============== RISCHIO COMEBACK -- {comebackCount} --  {current} ===================")
                        
                    else: # the comeback stops here

                        # reset counter, restart position and alert status
                        comebackAlert = False
                        comebackCount = 0
                        comebackStart = None
                        
                        # notify the user                        
                        logging.info(f"============== COMEBACK SCONGIURATO ===================")
                        
                else: # this is a new risk for comeback

                    if d_from_start < distance_from_start:

                        # start counting the number of consecutive comeback points
                        comebackCount += 1

                        # save the current position, because if we reach 5 consecutive
                        # comeback points, we start again from this point. Also save dir
                        comebackPosition = current
                        comebackDirection = mean_angle(history[-10:]) # lastDirection
                        logging.error(f"TREND DIRECTION SET TO {comebackDirection}")

                        # save the distance from start measured at this point
                        comebackStart = distance_from_start

                        # set the alert status
                        comebackAlert = True
                        
                        # notify the user
                        logging.info(f"============== RISCHIO COMEBACK -- {comebackCount} -- {current} ===================")
                    
                # update the distance from start point                                        
                distance_from_start = d_from_start
                
            else:

                logging.info("No suitable candidate found, exiting!")
                restart = True
                break
                                            
    except Exception as e:
        logging.error(f"Error during bathy analysis: {e}")
        raise

    return restart, current_lat, current_lon, mean_angle(history[-10:]), i, distance_from_start
