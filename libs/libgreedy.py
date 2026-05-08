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
# "Greedy algorithm" Function
#
#############################################################

def greedy_distance_to_end(
    start_node,
    end_node,
    node_neighbors,
    lats,
    lons,
    max_steps=10000
):

    """
    Estimate river-constrained distance from start_node
    to end_node using a greedy search strategy.
    """

    current = start_node
    visited = set()
    total_distance = 0.0
    steps = 0

    while current != end_node and steps < max_steps:

        steps += 1
        visited.add(current)

        neighbors = node_neighbors.get(current, [])

        best_neighbor = None
        best_dist = float("inf")

        for n in neighbors:

            if n in visited:
                continue

            # distance from candidate to end
            d = haversine(
                lats[n],
                lons[n],
                lats[end_node],
                lons[end_node]
            )

            if d < best_dist:
                best_dist = d
                best_neighbor = n

        if best_neighbor is None:
            # dead end
            return float("inf")

        # accumulate path length
        segment_distance = haversine(
            lats[current],
            lons[current],
            lats[best_neighbor],
            lons[best_neighbor]
        )

        total_distance += segment_distance

        current = best_neighbor

    return total_distance


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

