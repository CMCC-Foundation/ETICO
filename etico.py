#!/usr/bin/python

#############################################################
#
# Requirements
#
#############################################################

# global reqs
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from scipy.spatial import KDTree
import matplotlib.tri as mtri
import argparse
from collections import deque

# local reqs
from libs.libconfig import *
from libs.libplot import *


#############################################################
#
# Global variables
#
#############################################################

angles = {
    "E":0, "NE":45, "N":90, "NW":135, "W":180, "SW":225, "S":270, "SE": 315    
}


#############################################################
#
# "Get Neighbors" Function
#
#############################################################

def get_n_level_neighbors(start_node, node_neighbors, n):
    visited = set()
    level_nodes = set()
    queue = deque()
    queue.append((start_node, 0))
    visited.add(start_node)

    while queue:
        current_node, level = queue.popleft()
        if 0 < level <= n:
            level_nodes.add(current_node)
        if level < n:
            for neighbor in node_neighbors.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, level + 1))
    return level_nodes


#############################################################
#
# Optimisation Function
#
#############################################################

def refine_path_by_depth(path, depths, node_neighbors):
    new_path = path.copy()
    for i in range(1, len(path)-1):  # ignora il primo e ultimo punto
        current = path[i]
        neighbors = node_neighbors.get(current, [])

        # Trova il vicino con profondità maggiore del punto corrente
        best = current
        for n in neighbors:
            if depths[n] > depths[best]:
                best = n

        if best != current:
            new_path[i] = best
    return new_path


#############################################################
#
# Haversine Function
#
#############################################################

def haversine(lat1, lon1, lat2, lon2):

    """
    Calculates the great-circle distance in kilometers between two geographic 
    coordinates using the Haversine formula.
    """
    
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0)**2
    return R * 2 * np.arcsin(np.sqrt(a))


#############################################################
#
# "Angle Between" Function
#
#############################################################

def angle_between(lat1, lon1, lat2, lon2):

    """
    Computes the compass bearing (in degrees) from one geographic point to another.    
    """
    
    dy = lat2 - lat1
    dx = lon2 - lon1
    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad)
    return (angle_deg + 360) % 360


#############################################################
#
# "Angle Diff" Function
#
#############################################################

def angle_diff(a1, a2):
    return min(abs(a1 - a2), 360 - abs(a1 - a2))


#############################################################
#
# "Angle To Direction" Function
#
#############################################################

def angle_to_direction(angle):

    """
    Converts a compass angle (in degrees) into a cardinal or intercardinal 
    direction string (e.g. "N", "NE", "E", etc.).
    """
    
    directions = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
    idx = int(((angle + 22.5) % 360) / 45)
    return directions[idx]


#############################################################
#
# "Mean Angle" Function
#
#############################################################

def mean_angle(angles_deg):
    
    """
    Calculates the circular mean of a sequence of angles,
    correctly handling wrap-around at 360 deg.
    """
    
    if not angles_deg:
        return None
    angles_rad = np.radians(angles_deg)
    x = np.mean(np.cos(angles_rad))
    y = np.mean(np.sin(angles_rad))
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


#############################################################
#
# MAIN
#
#############################################################

if __name__ == "__main__":

    # read input params
    nc_file = sys.argv[1]
    config_file = sys.argv[2]
        
    # read config file
    config_dict = read_config_as_dict(config_file)

    start_point = (config_dict["Algorithm"]["startlat"], config_dict["Algorithm"]["startlon"])
    end_point = (config_dict["Algorithm"]["endlat"], config_dict["Algorithm"]["endlon"])
    initial_angle = angles[config_dict["Algorithm"]["startdir"]]
    max_steps = config_dict["Algorithm"]["maxsteps"]
    stop_distance_km = config_dict["Algorithm"]["stopdistance"]                                
    cbar_min = config_dict["Plot"]["cbarmin"]
    cbar_max = config_dict["Plot"]["cbarmax"]

    
    # ========== Weights ==========
    distance_weight = config_dict["Algorithm"]["distanceweight"]
    depth_weight = config_dict["Algorithm"]["depthweight"]
    direction_weight = config_dict["Algorithm"]["directionweight"]
    history_direction_weight = config_dict["Algorithm"]["historydirectionweight"]


    #############################################################
    #
    # Load Data
    #
    #############################################################
    
    ds = Dataset(nc_file)
    lats = ds.variables['latitude'][:]
    lons = ds.variables['longitude'][:]
    depths = ds.variables['total_depth'][:]
    elements = ds.variables['element_index'][:, :] - 1 
    
    coords = np.column_stack((lats, lons))
    kdtree = KDTree(coords)

    
    #############################################################
    #
    # Adjacency map 
    #
    #############################################################
    
    node_neighbors = {}
    for tri in elements:
        for i in range(3):
            n1, n2 = tri[i], tri[(i + 1) % 3]
            node_neighbors.setdefault(n1, set()).add(n2)
            node_neighbors.setdefault(n2, set()).add(n1)
    

    #############################################################
    #
    # Initialization
    #
    #############################################################

    original_start_idx = start_idx = kdtree.query(start_point)[1]
    end_idx = kdtree.query(end_point)[1]
    
    visited = set()
    path = [start_idx]
    current = start_idx
    last_angle = initial_angle
    angle_history = deque([initial_angle], maxlen=20)
    steps = 0
    approaching_start_count = 0
    prev_dist_to_start = haversine(lats[current], lons[current], lats[start_idx], lons[start_idx])
    prev_dist_to_end = haversine(lats[current], lons[current], lats[end_idx], lons[end_idx])
    reverse_start_node = None  # where the path starts to go far from the end point 
    
    
    #############################################################
    #
    # Algorithm
    #
    #############################################################

    while current != end_idx and steps < max_steps:
        steps += 1
        visited.add(current)


        # Calculate distance from start and end
        dist_to_end = haversine(lats[current], lons[current], lats[end_idx], lons[end_idx])
        dist_to_start = haversine(lats[current], lons[current], lats[start_idx], lons[start_idx])
        
        if dist_to_start < prev_dist_to_start and dist_to_end > prev_dist_to_end:
            approaching_start_count += 1
            if approaching_start_count == 1:
                reverse_start_node = current  # store where the problem appears
        else:            
            approaching_start_count = 0  # reset if pattern interrupts
            reverse_start_node = None            
        
        if approaching_start_count >= 5:

            print(f"\nWrong direction for {approaching_start_count} consecutive steps.")
            print(f"Restarting from node {reverse_start_node}")
            print(type(angle_history))
            for _ in range(5):
                angle_history.pop()
            
            # restart from reverse_start_node
            current = reverse_start_node
            start_idx = reverse_start_node
            visited = set()
            path = path[0:-5]    
            
            # reset counters
            approaching_start_count = 0
            reverse_start_node = None
        
            # update distances
            prev_dist_to_start = haversine(lats[current], lons[current], lats[start_idx], lons[start_idx])
            prev_dist_to_end = haversine(lats[current], lons[current], lats[end_idx], lons[end_idx])
            continue

        
        # update previous values for next step
        prev_dist_to_start = dist_to_start
        prev_dist_to_end = dist_to_end
                
        if dist_to_end <= stop_distance_km:
            print(f"Stopped: distance from target {dist_to_end:.3f} km <= {stop_distance_km} km")
            break
    
        # neighbors = get_neighbors(current, node_neighbors)


        neighbors = get_n_level_neighbors(current, node_neighbors, config_dict["Algorithm"]["radius"])
        
        best_score = float('inf')
        next_node = None
        best_angle = None
        avg_angle = mean_angle(angle_history)
    
        for n in neighbors:
            if n in visited:
                continue
            d = haversine(lats[n], lons[n], lats[end_idx], lons[end_idx])
            h = -depths[n]
            ang = angle_between(lats[current], lons[current], lats[n], lons[n])

            if last_angle is not None:
                penalty_last = angle_diff(last_angle, ang) / 180.0
            else:
                penalty_last = 0
            
            # penalty_last = angle_diff(last_angle, ang) / 180.0
            penalty_avg = angle_diff(avg_angle, ang) / 180.0 if avg_angle is not None else 0
    
            score = (
                distance_weight * d +
                depth_weight * h +
                direction_weight * penalty_last +
                history_direction_weight * penalty_avg
            )
    
            if score < best_score:
                best_score = score
                next_node = n
                best_angle = ang
    
        if next_node is None:
            print("Path stopped. No valid neighbor.")
            break
    
        direction = angle_to_direction(best_angle)
        print(f"Step {steps:3d}: from {current} to {next_node}, angle {best_angle:.1f}° ({direction}), distance from target {dist_to_end:.3f} km")
    
        last_angle = best_angle
        angle_history.append(best_angle)
        path.append(next_node)
        current = next_node

        
    #############################################################
    #
    # refine path
    #
    #############################################################

    refined_path = path
    counter = 0
    for i in range(config_dict["Algorithm"]["optimisationsteps"]):
        counter += 1
        refined_path_new = refine_path_by_depth(refined_path, depths, node_neighbors)
        refined_path = refined_path_new

        # Save thalweg to csv file
        outfile_name = os.path.join(config_dict["Output"]["outputdirectory"], "%s.%s" % (config_dict["Output"]["thalwegfile"], str(counter)))
        with open(outfile_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Latitude', 'Longitude', 'Depth'])
        
            for lat, lon, depth in zip(lats[refined_path], lons[refined_path], depths[refined_path]):
                writer.writerow([lat, lon, depth])
      
        
    
    #############################################################
    #
    # CSV output
    #
    #############################################################
        
    # Save thalweg to csv file
    outfile_name = os.path.join(config_dict["Output"]["outputdirectory"], config_dict["Output"]["thalwegfile"])
    with open(outfile_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Latitude', 'Longitude', 'Depth'])
        
        for lat, lon, depth in zip(lats[path], lons[path], depths[path]):
            writer.writerow([lat, lon, depth])
            
            
    #############################################################
    #
    # Plot
    #
    #############################################################

    plot(lons, lats, elements, depths, path, refined_path, original_start_idx, end_idx, config_dict)
