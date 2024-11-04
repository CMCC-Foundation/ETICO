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
    cardinal_to_angle_map = {
        'N': 0,
        'NE': 45,
        'E': 90,
        'SE': 135,
        'S': 180,
        'SW': 225,
        'W': 270,
        'NW': 315
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
        (337.5, 22.5): 'N',
        (22.5, 67.5): 'NE',
        (67.5, 112.5): 'E',
        (112.5, 157.5): 'SE',
        (157.5, 202.5): 'S',
        (202.5, 247.5): 'SW',
        (247.5, 292.5): 'W',
        (292.5, 337.5): 'NW'
    }

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


# ################################################
# #
# # get adjacent directions
# #
# ################################################

# def get_adjacent_directions(item, permissive=False):

#     directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

#     # Find the index of the item
#     index = directions.index(item)

#     # Get the previous and next items using modular arithmetic for cyclic behavior
#     previous_item = directions[(index - 1) % len(directions)]
#     next_item = directions[(index + 1) % len(directions)]

#     # If permissive is True, include two more adjacent items
#     if permissive:
#         previous_item_far = directions[(index - 2) % len(directions)]
#         next_item_far = directions[(index + 2) % len(directions)]
#         return [previous_item_far, previous_item, next_item, next_item_far]
    
#     # return
#     return [previous_item, next_item]


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



# ################################################
# #
# # get direction
# #
# ################################################

# def get_allowed_directions_complex_trend(trend, permissive=False):
#     """
#     Determine the allowed direction based on the complex trend
#     """

#     # find the number of occurrences for each direction
#     direction_counts = Counter(trend)
#     sorted_directions = dict(sorted(direction_counts.items(), key=lambda x: x[1], reverse=True))


#     # Calculate percentage and store it along with counts in an ordered dictionary
#     sorted_directions_with_percentage = {
#         direction: {
#             'count': count,
#             'percentage': (count / len(trend)) * 100
#         }
#         for direction, count in sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)
#     }
    
#     # start building a list of allowed direction by
#     # putting the most frequent with a maximum score (e.g. N:9)
#     # and its adjacent ones with lower score (e.g. NE: and NW:)
#     allowed_directions = []
#     for direction, stats in sorted_directions_with_percentage.items():
        
#         # if the list is still empty, add the most frequent
#         # item, no matter its percentage
#         if len(allowed_directions) == 0:
#             allowed_directions.append(direction)
#             adj = get_adjacent_directions(direction, permissive)
#             for el in adj:
#                 allowed_directions.append(el)

#         # consider all the other occurrences after the first
#         else:
#             if stats["percentage"] >= 30:
#                 if not direction in allowed_directions:
#                     allowed_directions.append(direction)
#                 adj = get_adjacent_directions(direction, permissive)
#                 for el in adj:
#                     if not el in allowed_directions:
#                         allowed_directions.append(el)
#             else:
#                 break    
    
#     return allowed_directions



# ################################################
# #
# # get direction
# #
# ################################################

# def get_allowed_directions_unified(trend, lastDirection, permissive=False):
#     """
#     Determine the allowed direction based on the complex trend
#     """

#     # find the number of occurrences for each direction
#     direction_counts = Counter(trend)
#     sorted_directions = dict(sorted(direction_counts.items(), key=lambda x: x[1], reverse=True))


#     # Calculate percentage and store it along with counts in an ordered dictionary
#     sorted_directions_with_percentage = {
#         direction: {
#             'count': count,
#             'percentage': (count / len(trend)) * 100
#         }
#         for direction, count in sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)
#     }


#     # ======= Create the list of the trend-allowed directions =======

#     allowed_directions = []            
#     if trend:
    
#         # start building a list of allowed direction by
#         # putting the most frequent with a maximum score (e.g. N:9)
#         # and its adjacent ones with lower score (e.g. NE: and NW:)
#         for direction, stats in sorted_directions_with_percentage.items():
            
#             # if the list is still empty, add the most frequent
#             # item, no matter its percentage
#             if len(allowed_directions) == 0:
#                 allowed_directions.append(direction)
#                 adj = get_adjacent_directions(direction, permissive)
#                 for el in adj:
#                     allowed_directions.append(el)
    
#             # consider all the other occurrences after the first
#             else:
#                 if stats["percentage"] >= 30:
#                     if not direction in allowed_directions:
#                         allowed_directions.append(direction)
#                     adj = get_adjacent_directions(direction, permissive)
#                     for el in adj:
#                         if not el in allowed_directions:
#                             allowed_directions.append(el)
#                 else:
#                     break    
                
#     # ======= Create the scores based on the last direction =======

#     scores = { "N": 0, "NE": 0, "E": 0, "SE": 0, "S": 0, "SW": 0, "W": 0, "NW": 0 }
#     dir_last = get_adjacent_directions(lastDirection, True)
#     scores[dir_last[0]] = 1
#     scores[dir_last[1]] = 5
#     scores[dir_last[2]] = 5
#     scores[dir_last[3]] = 1
#     scores[lastDirection] = 9

#     # ======= Sum 10 to the score for each direction in the trend-allowed dirs =======

#     for d in scores.keys():
#         if d in allowed_directions:
#             scores[d] += 10

#     # return
#     return scores




# ################################################
# #
# # get direction
# #
# ################################################

# def get_direction(current_idx, target_idx):
#     """
#     Determine the direction from the current index to the target index.
#     """
#     d_lat = target_idx[0] - current_idx[0]
#     d_lon = target_idx[1] - current_idx[1]

#     # if d_lat == 0 and d_lon > 0:
#     #     return "E"
#     # elif d_lat == 0 and d_lon < 0:
#     #     return "W"
#     # elif d_lat > 0 and d_lon == 0:
#     #     return "S"
#     # elif d_lat < 0 and d_lon == 0:
#     #     return "N"
#     # elif d_lat > 0 and d_lon > 0:
#     #     return "SE"
#     # elif d_lat > 0 and d_lon < 0:
#     #     return "SW"
#     # elif d_lat < 0 and d_lon > 0:
#     #     return "NE"
#     # elif d_lat < 0 and d_lon < 0:
#     #     return "NW"
#     # else:
#     #     return "Unknown"
    
#     if d_lat == 0 and d_lon > 0:
#         return "E"
#     elif d_lat == 0 and d_lon < 0:
#         return "W"
#     elif d_lat > 0 and d_lon == 0:
#         return "N"
#     elif d_lat < 0 and d_lon == 0:
#         return "S"
#     elif d_lat > 0 and d_lon > 0:
#         return "NE"
#     elif d_lat > 0 and d_lon < 0:
#         return "NW"
#     elif d_lat < 0 and d_lon > 0:
#         return "SE"
#     elif d_lat < 0 and d_lon < 0:
#         return "SW"
#     else:
#         return "Unknown"


# ################################################
# #
# # direction similarity
# #
# ################################################
    
# def direction_similarity(direction1, direction2):
#     """
#     Measure the similarity between two directions.
#     """

#     vector1 = DIRECTIONS.get(direction1, (0, 0))
#     vector2 = DIRECTIONS.get(direction2, (0, 0))
#     dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]

#     return dot_product









# ################################################
# #
# # direction distance score
# #
# ################################################

# def direction_distance_score(dir1, dir2, trend=None):
#     """
#     Calculate the minimal angular distance between two compass directions and assign a score inversely proportional to the distance.

#     Parameters:
#     - dir1: str, first direction (e.g., 'N', 'NE', 'E', etc.)
#     - dir2: str, second direction

#     Returns:
#     - minimal_distance_steps: int, minimal number of steps between directions
#     - minimal_distance_degrees: int, minimal angular distance in degrees
#     - score: float, score inversely proportional to the angular distance
#     """
#     directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
#     direction_map = {direction: index for index, direction in enumerate(directions)}
    
#     # Validate input directions
#     if dir1 not in direction_map or dir2 not in direction_map:
#         raise ValueError("Invalid direction. Choose from 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'.")
    
#     idx1 = direction_map[dir1]
#     idx2 = direction_map[dir2]
    
#     # Compute absolute difference
#     diff = abs(idx1 - idx2)
    
#     # Since the list is cyclic, the minimal distance is the smaller between
#     # the direct difference and the wrap-around difference
#     minimal_steps = min(diff, len(directions) - diff)
    
#     # Each step represents 45 degrees
#     minimal_distance_degrees = minimal_steps * 45

#     # Calculate score inversely proportional to degrees
#     # Handle the case where degrees = 0 to avoid division by zero
#     if minimal_distance_degrees == 0:
#         score = 1.0  # Assign maximum score when directions are the same
#     else:
#         score = 1 / minimal_distance_degrees  # Inverse proportionality

#     # check if we are in the range of 180 degrees centered on the direction
#     if trend:
#         if minimal_distance_degrees > 45:
#             score = 0
#     else:
#         if minimal_distance_degrees > 90:
#             score = 0        
        
#     # Optional: Normalize the score to a range (e.g., 0 to 1)
#     # For example, maximum possible score is when degrees = 0 (score = 1.0)
#     # Minimum possible score is when degrees = 180 (score = 1/180 ≈ 0.0056)
#     # If desired, you can scale the score differently
#     return minimal_steps, minimal_distance_degrees, score








# ################################################
# #
# # lastdir score
# #
# ################################################

# def get_lastdir_score(dir1, dir2):

#     directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
#     direction_map = {direction: index for index, direction in enumerate(directions)}
    
#     # Validate input directions
#     if dir1 not in direction_map or dir2 not in direction_map:
#         raise ValueError("Invalid direction. Choose from 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'.")
    
#     idx1 = direction_map[dir1]
#     idx2 = direction_map[dir2]
    
#     # Compute absolute difference
#     diff = abs(idx1 - idx2)
    
#     # Since the list is cyclic, the minimal distance is the smaller between
#     # the direct difference and the wrap-around difference
#     minimal_steps = min(diff, len(directions) - diff)
    
#     # Each step represents 45 degrees
#     minimal_distance_degrees = minimal_steps * 45

#     # Calculate score inversely proportional to degrees
#     # Handle the case where degrees = 0 to avoid division by zero
#     if minimal_distance_degrees == 0:
#         score = 0  # Assign maximum score when directions are the same
#     else:
#         score = minimal_distance_degrees  # Inverse proportionality

#     # return the score
#     return score







# ################################################
# #
# # find_most_frequent_direction
# #
# ################################################

# def find_most_frequent_direction(directions):

#     """
#     Determine the most frequent direction from a list of directions.
#     """

#     if not directions:
#         return None
#     counter = Counter(directions)
#     most_common = counter.most_common(1)
#     return most_common[0][0] if most_common else None




# ################################################
# #
# # get trend score
# #
# ################################################

# def get_trend_score(trend, direction):

#     # if we are in the init phase, we skip this
#     if len(trend) <= 10:
#         return 0
    
#     else:
#         pass



################################################
#
# print neighborhood
#
################################################

def print_neighborhood(current_lat_idx, current_lon_idx, bathy, lat_min, lat_max, lon_min, lon_max, candidates, selected):
    
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
                    cell = f"{rounded_value} ({str(g1_score)}, {str(g2_score)}, {str(g3_score)})"
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
        
    # Stampa la tabella con le righe in ordine inverso per mantenere l'orientamento corretto
    # for el in rows[::-1]:
    #     logging.info(el)

    # for el in srows[::-1]:
    #     logging.info(el)

    table = tabulate(
        trows
    )
    print(table)
    
    # print(candidates)
    
    # rows = []
    # for lat_idx in range(lat_min, lat_max):
    #     row = []
    #     for lon_idx in range(lon_min, lon_max):

    #         # costruisci un dizionario dei candidati
    #         candict = {f"{candidate['lat_idx']}{candidate['lon_idx']}": candidate for candidate in candidates}
            
    #         # Recupera il valore della profondità
    #         value = bathy[lat_idx, lon_idx]
    #         rounded_value = round(value, 3) if not np.isnan(value) else "NaN"
    #         formatted_value = f"{rounded_value:>8}"

    #         # check if we have the angle
    #         if f"{lat_idx}{lon_idx}" in candict.keys():
    #             logging.info(candict[f"{lat_idx}{lon_idx}"]["angle"])
    #             angle = candict[f"{lat_idx}{lon_idx}"]["angle"]
    #             if angle:
    #                 row.append(f"{formatted_value} ({angle})")
    #             else:
    #                 row.append(f"{formatted_value}")
    #         else:
    #             row.append("BOH")
                    
    #         # else:
    #         #     row.append(formatted_value_with_angle = f"{formatted_value}")
                
    #         # row.append(colored(f"{formatted_value}", 'green'))


    #         # # Controlla se la cella è il punto selezionato
    #         # if (lat_idx, lon_idx) == selected:
    #         #     row.append(colored(f"{formatted_value}", 'green'))
            
    #         # # Controlla se la cella è un candidato
    #         # elif (lat_idx, lon_idx) in [(lat, lon) for lat, lon, _ in candidates]:
    #         #     # Recupera l'angolo del candidato specifico
    #         #     angle = next((angle for lat, lon, angle in candidates if (lat, lon) == (lat_idx, lon_idx)), None)
    #         #     formatted_value_with_angle = f"{formatted_value} ({angle}°)"

    #         #     # Aggiungi l'asterisco se la cella è il punto selezionato
    #         #     if (lat_idx, lon_idx) == (selected[0], selected[1]):
    #         #         row.append(colored(formatted_value_with_angle, 'green', attrs=["bold"]))
    #         #     else:
    #         #         row.append(colored(formatted_value_with_angle, 'green'))

    #         # # Per le altre celle
    #         # else:
    #         #     row.append(formatted_value)
                
    #     rows.append(" ".join(row))

    # # Stampa la griglia al contrario per mantenere l'orientamento corretto
    # for el in rows[::-1]:
    #     logging.info(el)

        
# def print_neighborhood(bathy, lat_min, lat_max, lon_min, lon_max, candidates, selected):
#     """
#     Print the neighborhood grid, highlighting candidates and the selected one.
#     """

#     rows = []
#     for lat_idx in range(lat_min, lat_max):
#         row = []
#         for lon_idx in range(lon_min, lon_max):
#             value = bathy[lat_idx, lon_idx]
#             rounded_value = round(value, 3) if not np.isnan(value) else "NaN"
#             formatted_value = f"{rounded_value:>8}"
#             if (lat_idx, lon_idx) == selected:
#                 row.append(colored(f"{formatted_value}", 'green'))
#             elif (lat_idx, lon_idx) in [(lat, lon) for lat, lon, _ in candidates]:

#                 # Check if this cell is the selected one and append an asterisk
#                 if selected:
                
#                     if (lat_idx, lon_idx) == (selected[0], selected[1]):
#                         row.append(colored(formatted_value, 'green', attrs=["bold"]))
#                     else:
#                         row.append(colored(formatted_value, 'green'))
                               
#             else:
#                 row.append(formatted_value)
#         rows.append(" ".join(row))

#     for el in rows[::-1]:
#         logging.info(el)
    
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

        
# ################################################
# #
# # find_highest_bathy
# #
# ################################################

# def find_highest_bathy(ds, config):

#     """
#     Find the highest bathy point in the neighborhood of size windowSize
#     around the given start latitude and longitude. Save the path taken in a CSV file.
#     """
#     try:
#         bathy = ds['bathy'].values
        
#         # Start from the initial coordinates and find the closest grid cell indices
#         current_lat_idx, current_lon_idx = find_closest_index(ds, config['Input']['startLat'], config['Input']['startLon'])
        
#         # Output CSV file setup
#         csv_path = os.path.join(config['Output']['baseFolder'], config['Output']['thalwegCsvFile'])
#         with open(csv_path, mode='w', newline='') as csvfile:
#             csv_writer = csv.writer(csvfile)
#             csv_writer.writerow(['Latitude', 'Longitude', 'Depth', 'Direction'])
            
#             # Write the starting point to the CSV without rounding
#             start_depth = bathy[current_lat_idx, current_lon_idx]
#             csv_writer.writerow([config['Input']['startLat'], config['Input']['startLon'], start_depth, "None"])

#         # Keep track of visited cells
#         visited_cells = set()
#         directions_taken = []
#         last_direction = config['Input']['initialDirection']

#         # ====== Start main loop ======

#         lastDirection = config['Input']['initialDirection']
#         retry = False
#         for i in range(config['Input']['maxIterations']):

#             # ====== Get current item and see if we're close to the end point ======
            
#             # Get the current latitude, longitude, and depth
#             current_lat = ds['lat'].values[current_lat_idx]
#             current_lon = ds['lon'].values[current_lon_idx]
#             current_depth = bathy[current_lat_idx, current_lon_idx]

#             logging.info("\n")
#             logging.info(f"Iteration {i + 1}: Current Position {current_lat}, {current_lon}, Indices: ({current_lat_idx}, {current_lon_idx})")
#             logging.info(directions_taken[-10:])
#             logging.info(last_direction)            
            
#             # Check if the current position is close to the endpoint
#             distance_to_end = calculate_distance(current_lat, current_lon, config["Input"]["endLat"], config["Input"]["endLon"])
#             if distance_to_end <= config["Input"]["endDistance"]:
#                 logging.info(f"Reached endpoint proximity: {distance_to_end:.2f} meters from the target point. Stopping.")
#                 break

#             # Write the current position to the CSV without rounding
#             with open(csv_path, mode='a', newline='') as csvfile:
#                 csv_writer = csv.writer(csvfile)
#                 csv_writer.writerow([current_lat, current_lon, current_depth, directions_taken[-1] if directions_taken else "None"])
                
#             # Mark the current cell as visited by setting its value to NaN
#             bathy[current_lat_idx, current_lon_idx] = np.nan
#             visited_cells.add((current_lat_idx, current_lon_idx))

#             # ====== Determine neighborhood ======
            
#             # Determine the neighborhood bounds based on full window size
#             if retry:
#                 half_window = config['Input']['windowSize']+4 // 2 # increase the window size
#             else:
#                 half_window = config['Input']['windowSize'] // 2
                
                
#             lat_min = max(0, current_lat_idx - half_window)
#             lat_max = min(bathy.shape[0], current_lat_idx + half_window + 1)
#             lon_min = max(0, current_lon_idx - half_window)
#             lon_max = min(bathy.shape[1], current_lon_idx + half_window + 1)

#             # # ====== find candidates based on depth ======
            
#             # # Find the highest bathy in the neighborhood, considering tolerance and direction
#             # highest_bathy = -np.inf
#             # candidates = []

#             # for lat_idx in range(lat_min, lat_max):
#             #     for lon_idx in range(lon_min, lon_max):
#             #         if not np.isnan(bathy[lat_idx, lon_idx]):
#             #             if bathy[lat_idx, lon_idx] >= highest_bathy - config['Input']['depthTolerance']:
#             #                 highest_bathy = max(highest_bathy, bathy[lat_idx, lon_idx])
#             #                 candidates.append((lat_idx, lon_idx, bathy[lat_idx, lon_idx]))                            

#             # # Filter candidates within the tolerance range
#             # candidates = [(lat, lon, val) for lat, lon, val in candidates if val >= highest_bathy - config['Input']['depthTolerance']]

#             # if not candidates:
#             #     logging.info("All points in the neighborhood are visited or NaN; stopping.")
#             #     break

#             # # ====== Determine score of directions for this iteration ======
            
#             # # initialise the best candidate
#             # preferred_direction = config['Input']['initialDirection'] if i < config['Input']['initPhase'] else last_direction
#             # best_candidate = None
#             # best_similarity = np.inf
            
#             # # debug message: print the allowed directions based on trend:            
#             # allowed_dirs_trend = get_allowed_directions_complex_trend(directions_taken[-10:])
#             # logging.info(f"Allowed directions by complex trend: {allowed_dirs_trend}")

#             # # debug message: print the allowed directions based on last movement (if any)
#             # if i > 0:
#             #     allowed_dirs_last = get_adjacent_directions(lastDirection, True)
#             #     allowed_dirs_last.append(lastDirection)
#             # else:
#             #     allowed_dirs_last = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']             
#             # logging.info(f"Allowed directions by last direction: {allowed_dirs_last}")

#             # # calculate the score --- G FUNCTION
#             # if i >= 10:
#             #     score = get_allowed_directions_unified(directions_taken[-10:], directions_taken[-1:][0], permissive=False)
#             # else:
#             #     score = get_allowed_directions_unified([], lastDirection, permissive=False)
#             # logging.info(f"{score}")

            
#             ##########################################################
#             # ATTEMPT OF NEW EURISTIC == start
#             ##########################################################

#             # iterate over the cells
            
#             # Find the highest bathy in the neighborhood, considering tolerance and direction
#             highest_bathy = -np.inf
#             candidates = []

#             # first of all, look for the maximum bathymetry value
#             for lat_idx in range(lat_min, lat_max):
#                 for lon_idx in range(lon_min, lon_max):
                    
#                     # if the current point is not nan and is deeper than the current max, update the max!
#                     if not np.isnan(bathy[lat_idx, lon_idx]):
#                         if bathy[lat_idx, lon_idx] >= highest_bathy:
#                             highest_bathy = bathy[lat_idx, lon_idx]
                            
#             # now iterate on all the items and assign a score
#             for lat_idx in range(lat_min, lat_max):
#                 for lon_idx in range(lon_min, lon_max):

#                     # if the current point is not nan and is in max-tolerance range, assign 0. Otherwise 1
#                     if not np.isnan(bathy[lat_idx, lon_idx]):

                        
#                         candidate_direction = get_direction((current_lat_idx, current_lon_idx), (lat_idx, lon_idx))
#                         # trend_score = direction_distance_score(directions[-10:], candidate_direction)
                        
                        
#                         if bathy[lat_idx, lon_idx] >= highest_bathy - config['Input']['depthTolerance']:                            
#                             # calculate the three components of the G score
#                             weight_score = 0
#                             lastdir_score = get_lastdir_score(lastDirection, candidate_direction)
#                             # trend_score = get_trend_score()

#                             # calculate G
#                             g = 0 + lastdir_score

#                             # calculate H
#                             h = distance_to_end

#                             # calculate F = G + H
#                             f = g + h
#                             candidates.append((lat_idx, lon_idx, bathy[lat_idx, lon_idx], f))
                            
#                         else:

#                             # calculate the three components of the G score
#                             weight_score = 1
#                             lastdir_score = get_lastdir_score(lastDirection, candidate_direction)
#                             # trend_score = get_trend_score()

#                             # calculate G
#                             g = 1 + lastdir_score

#                             # calculate H
#                             h = distance_to_end

#                             # calculate F = G + H
#                             f = g + h
#                             candidates.append((lat_idx, lon_idx, bathy[lat_idx, lon_idx], f))                            

#             # find the best candidate
#             best_score = np.inf
#             best_candidate = None
#             for c in candidates:
                
                
#                 if c[3] < best_score:
#                     logging.info(f"Updating best from {best_score} to {c[3]}")
#                     best_score = c[3]
#                     best_candidate = c
#                     logging.info(f"Updated best to {best_score}")
#                 logging.info(f"Candidate: {c[0]}, {c[1]} -- Depth: {c[2]} -- Score: {c[3]}")
            
#             logging.info(f"Best candidate is {best_candidate[0]}, {best_candidate[1]} -- Depth: {best_candidate[2]} -- Score: {best_candidate[3]}")
                
                            
#             # ##########################################################
#             # # ATTEMPT OF NEW EURISTIC == end
#             # ##########################################################

            
#             # # ======= Assign a score to the candidates =======

#             # # initialize current score
#             # currentScore = 0
                        
#             # # iterate over candidates
#             # good_candidates = []
#             # logging.info("Candidates:")            
#             # for lat_idx, lon_idx, val in candidates:

#             #     # get the direction of the new candidate
#             #     direction = get_direction((current_lat_idx, current_lon_idx), (lat_idx, lon_idx))
                                    
#             #     # Print direction along with other details
#             #     candidate_info = f"Lat: {float(ds['lat'][lat_idx])}, Lon: {float(ds['lon'][lon_idx])}, " \
#             #         f"Indices: ({lat_idx}, {lon_idx}) - " \
#             #         f"Depth: {np.round(val, 3)}, Direction: {direction}, Score: {score[direction]}"
                
#             #     ### Should be updated the best candidate?
#             #     if score[direction] > currentScore:
#             #         currentScore = score[direction]
#             #         best_candidate = (lat_idx, lon_idx, direction)
                                                                                   
#             #     logging.info(colored(candidate_info, 'green' if (lat_idx, lon_idx) == best_candidate else None))
            
#             # # Log the neighborhood
#             # try:
#             #     print_neighborhood(bathy, lat_min, lat_max, lon_min, lon_max, candidates, best_candidate)
#             # except:
#             #     logging.error(traceback.print_exc())
#             #     pdb.set_trace()
                
#             # for lat_idx, lon_idx, val in candidates:
#             #     direction = get_direction((current_lat_idx, current_lon_idx), (lat_idx, lon_idx))
#             #     similarity_to_last = direction_similarity(direction, preferred_direction)
#             #     similarity_to_frequent = direction_similarity(direction, most_frequent_direction) if most_frequent_direction else 0
#             #     score = similarity_to_last + similarity_to_frequent
#             #     candidate_info = f"Lat: {np.round(float(ds['lat'][lat_idx]), 3)}, Lon: {np.round(float(ds['lon'][lon_idx]), 3)}, Score: {score} (Last: {similarity_to_last}, Last10: {similarity_to_frequent})"

#             #     if score > best_similarity:
#             #         best_similarity = score
#             #         best_candidate = (lat_idx, lon_idx, direction)

#                 # logging.info(colored(candidate_info, 'green' if (lat_idx, lon_idx) == best_candidate else None))

#             if len(candidates) == 0:
#                 logging.info("No suitable candidate found; stopping (1).")
#                 break


#             sys.exit()
            
#             # if not best_candidate:
#             #     logging.info("No suitable candidate found; stopping (2).")
#             #     break

#             ##########################################################
#             # ATTEMPT OF RELAXATION == start
#             ##########################################################

#             if not best_candidate:

#                 if not retry:
                
#                     logging.error(colored("ERROR -- retrying", "red", attrs=["bold"]))
#                     retry = True
#                     i = i - 1
#                     continue

#                 else:
#                     logging.error(colored("ERROR -- retrying failed -- stopping", "red", attrs=["bold"]))
#                     break
                
#             else:
#                 retry = False
                
#             ##########################################################
#             # ATTEMPT OF RELAXATION == end
#             ##########################################################


#             if best_candidate:
#                 highest_lat_idx, highest_lon_idx, chosen_direction, score = best_candidate
#                 selected_lat = ds['lat'].values[highest_lat_idx]
#                 selected_lon = ds['lon'].values[highest_lon_idx]
#                 selected_depth = bathy[highest_lat_idx, highest_lon_idx]
                
#                 # Log selected cell details
#                 logging.info(f"Selected cell: Lat: {float(selected_lat)}, Lon: {float(selected_lon)}, "
#                              f"Indices: ({highest_lat_idx}, {highest_lon_idx}), Depth: {selected_depth}")
            
#             highest_lat_idx, highest_lon_idx, chosen_direction = best_candidate
#             # Log and update the direction
#             logging.info(f"Moving direction: {chosen_direction}")
#             directions_taken.append(chosen_direction)
#             last_direction = chosen_direction

#             # Move to the cell with the highest bathy
#             current_lat_idx = highest_lat_idx
#             current_lon_idx = highest_lon_idx

#             # update last direction
#             lastDirection = chosen_direction
            

#             # if best_candidate:
#             #     highest_lat_idx, highest_lon_idx, chosen_direction = best_candidate
#             #     selected_lat = ds['lat'].values[highest_lat_idx]
#             #     selected_lon = ds['lon'].values[highest_lon_idx]
#             #     selected_depth = bathy[highest_lat_idx, highest_lon_idx]
                
#             #     # Log selected cell details
#             #     logging.info(f"Selected cell: Lat: {float(selected_lat)}, Lon: {float(selected_lon)}, "
#             #                  f"Indices: ({highest_lat_idx}, {highest_lon_idx}), Depth: {selected_depth}")
            
#             # highest_lat_idx, highest_lon_idx, chosen_direction = best_candidate
#             # # Log and update the direction
#             # logging.info(f"Moving direction: {chosen_direction}")
#             # directions_taken.append(chosen_direction)
#             # last_direction = chosen_direction

#             # # Move to the cell with the highest bathy
#             # current_lat_idx = highest_lat_idx
#             # current_lon_idx = highest_lon_idx

#             # # update last direction
#             # lastDirection = chosen_direction
                        
#         # Log all directions taken
#         logging.info("Directions taken during the iterations:")
#         logging.info(directions_taken)

#     except Exception as e:
#         logging.error(f"Error during bathy analysis: {e}")
#         raise


################################################
#
# REFACTORING === find_highest_bathy
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
        csvfile = open(csv_path, mode='w', newline='')
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Latitude', 'Longitude', 'Depth', 'Direction'])
            
        # Write the starting point to the CSV without rounding
        start_depth = bathy[current_lat_idx, current_lon_idx]
        csv_writer.writerow([config['Input']['startLat'], config['Input']['startLon'], start_depth, "None"])

        # Keep track of visited cells
        visited_cells = set()
        history = []
        last_direction = config['Input']['initialDirection']

        # ====== Start main loop ======

        # make a copy of the original bathymetry to work on that
        working_bathy = bathy.copy()
       
        # read the angle related to initial direction
        lastDirection = cardinal_to_angle(config['Input']['initialDirection'])
        
        for i in range(config['Input']['maxIterations']):

            # debug message
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
            logging.info(f"Trend direction is {np.mean(history[-10:])}")
                            
            # now iterate to process the candidates            
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
                    
                    # # determine g-component depth_score
                    # if float(candidate["depth"]) <= float(highest_bathy) - float(config['Input']['depthTolerance']):
                    #     depth_score = 1
                    #     continue
                    # else:
                    #     depth_score = 0
                    depth_score = 1 / float(candidate["depth"])
                    
                    # determine g-component "last direction"
                    bearing = calculate_geodetic_bearing(current_lat, current_lon, ds['lat'][lat_idx], ds['lon'][lon_idx])
                    angle_score = np.abs(bearing - lastDirection)
                    # angle_score = multiply_score(angle_score)

                    # determine g-component "trend direction"
                    if len(history) >= 10:
                        trend_score = np.abs(bearing - np.mean(history[-10:]))
                        trend_score = multiply_score(trend_score)
                    else:
                        trend_score = 0
                                                        
                    # determine g
                    g = depth_score + 0.1 * angle_score + trend_score

                    candidate["g1_score"] = normalise(depth_score, 0, highest_bathy)
                    candidate["g2_score"] = normalise(angle_score, 0, 359)
                    candidate["g3_score"] = normalise(trend_score, 0, 359)
                    g = candidate["g1_score"] + candidate["g2_score"] + candidate["g3_score"]
                    
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
                print_neighborhood(current_lat_idx, current_lon_idx, working_bathy, lat_min, lat_max, lon_min, lon_max, candidates, None)
            except:
                logging.error(traceback.print_exc())
                pdb.set_trace()
                    
            # did we find a candidate?
            if best_candy:

                # debug message
                logging.info(f"SELECTED: {best_candy}")
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
                
            else:

                logging.info("No suitable candidate found, exiting!")
                break

                
                            
    except Exception as e:
        logging.error(f"Error during bathy analysis: {e}")
        raise
