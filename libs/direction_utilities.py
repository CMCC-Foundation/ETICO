#!/usr/bin/env python3

# global reqs
import sys
import pdb
from collections import Counter

# local reqs
from libs.print_utilities import *
from libs.exceptions import *

    
#########################################################
#
# get_min_through_zonal_direction
#
#########################################################

def get_direction_str(shift_coords):
    
    """Identifies the direction of the next movement
    
    Parameters
    ----------
    shift_coords: list
        A two-elements list with lat shift and lon shift
    
    Returns
    -------
    string
        a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    """
    
    # initialize the direction string
    dirString = ""
    
    # get latShift and lonShift
    latShift = shift_coords[0] 
    lonShift = shift_coords[1]
    medianIndex = 0
    
    # check the lat
    if shift_coords[0] < medianIndex:
        dirString = "S"
    elif shift_coords[0] > medianIndex:
        dirString = "N"
    
    # check the lon
    if shift_coords[1] > medianIndex:
        dirString = "%sE" % dirString
    elif shift_coords[1] < medianIndex:
        dirString = "%sW" % dirString
    
    # return
    return dirString


#########################################################
#
# get_acceptable_dir
#
#########################################################

def get_acceptable_dir(direc):
    
    """Identifies the direction of the next movement
    
    Parameters
    ----------
    direc: string
        a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    
    Returns
    -------
    list
        a list of the acceptable directions
    """
    
    if direc == "N":
        return ["W", "NW", "N", "NE", "E"]
        # return ["NW", "N", "NE"]
    elif direc == "NE":
        return ["NW", "N", "NE", "E", "SE"]
        # return ["N", "NE", "E"]
    elif direc == "E":
        return ["N", "NE", "E", "SE", "S"]
        # return ["NE", "E", "SE"]
    elif direc == "SE":
        return ["NE", "E", "SE", "S", "SW"]
        # return ["E", "SE", "S"]
    if direc == "S":
        return ["E", "SE", "S", "SW", "W"]
        # return ["SE", "S", "SW"]
    elif direc == "SW":
        return ["SE", "S", "SW", "W", "NW"]
        # return ["S", "SW", "W"]
    elif direc == "W":
        return ["S", "SW", "W", "NW", "N"]
        # return ["W", "SW", "S"]
    elif direc == "NW":
        return ["SW", "W", "NW", "N", "NE"]
        # return ["W", "NW", "N"]
    else:
        raise InvalidZonalDirectionException()
        sys.exit(101)


#########################################################
#
# get_direction_rank
#
#########################################################

def get_direction_rank(dir, lastdir):
    
    """Identifies the direction of the next movement
    
    Parameters
    ----------
    dir: string
        the next direction a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    lastdir: string
        the last direction, a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    
    Returns
    -------
    list
        a list of the acceptable directions
    """
        
    if lastdir == "N":
        scores = {"N": 9, "NE": 5, "E": 1, "SE": 0, "S": 0, "SW": 0, "W": 1, "NW": 5}
        
    elif lastdir  == "NE":
        scores = {"N": 5, "NE": 9, "E": 5, "SE": 1, "S": 0, "SW": 0, "W": 0, "NW": 1}
        
    elif lastdir  == "E":
        scores = {"N": 1, "NE": 5, "E": 9, "SE": 5, "S": 1, "SW": 0, "W": 0, "NW": 0}
        
    elif lastdir  == "SE":
        scores = {"N": 0, "NE": 1, "E": 5, "SE": 9, "S": 5, "SW": 1, "W": 0, "NW": 0}
        
    elif lastdir  == "S":
        scores = {"N": 0, "NE": 0, "E": 1, "SE": 5, "S": 9, "SW": 5, "W": 1, "NW": 0}

    elif lastdir  == "SW":
        scores = {"N": 0, "NE": 0, "E": 0, "SE": 1, "S": 5, "SW": 9, "W": 5, "NW": 1}

    elif lastdir  == "W":
        scores = {"N": 1, "NE": 0, "E": 0, "SE": 0, "S": 1, "SW": 5, "W": 9, "NW": 5}

    elif lastdir  == "NW":
        scores = {"N": 5, "NE": 1, "E": 0, "SE": 0, "S": 0, "SW": 1, "W": 5, "NW": 9}
    else:
        raise(InvalidZonalDirectionException)
        sys.exit(101)
        
    # return
    return scores[dir]



#########################################################
#
# get_trend
#
#########################################################

def get_trend(directionList):
    
    """Identifies the trend of the direction
    
    Parameters
    ----------
    directionList: list
        list of all the directions (strings among "NE", "N", "NW", "E", "W", "SE", "S", "SW")
        
    Returns
    -------
    str
        a string direction telling the trend
    dict
        a complex data structure summarising all the information on directions
    """
 
    # get the last 10 directions
    if len(directionList) < 10:
        workList = directionList
    else:   
        workList = directionList[-10:]

    # get the most common element in unsplitted list
    directionCount = Counter(workList)
    mostCommonDirections = directionCount.most_common()
    mostCommonDirection = mostCommonDirections[0][0]

    # now remove the "simple" directions and split the "complex" ones
    workList_split = []
    for string in workList:
        if len(string) > 1:
            for char in string:
                workList_split.append(char)
        
    # get the most common element in splitted list
    directionCountSplit = Counter(workList_split)
    mostCommonDirectionsSplit = directionCountSplit.most_common()
    # mostCommonDirectionSplit = mostCommonDirectionsSplit[0][0]

    # convert both the lists to dicts
    mostCommonDirectionsDict = {key: value for key, value in mostCommonDirections}
    mostCommonDirectionsSplitDict = {key: value for key, value in mostCommonDirectionsSplit}

    # now sum the components of the second list to the first one (multiplied by 0.5)
    for el in mostCommonDirectionsSplitDict.keys():
        if el in mostCommonDirectionsDict.keys():
            mostCommonDirectionsDict[el] += 0.5 * mostCommonDirectionsSplitDict[el]
        else:
            mostCommonDirectionsDict[el] = 0.5 * mostCommonDirectionsSplitDict[el]
                        
    # the trend is:
    return mostCommonDirection, mostCommonDirectionsDict



    # # get the last 10 directions
    # if len(directionList) < 10:
    #     workList = directionList
    # else:   
    #     workList = directionList[-10:]

    # # split directions (e.g. SW -> S, W)
    # workList_split = [char for string in workList for char in string]
        
    # # get the most common element in unsplitted list
    # string_counts = Counter(workList)
    # most_common_strings_u = string_counts.most_common()
    # most_common_string_u = most_common_strings_u[0][0]

    # # get the most common element in splitted list
    # string_counts = Counter(workList_split)
    # most_common_strings = string_counts.most_common()
    # most_common_string = most_common_strings[0][0]

    # # the trend is:
    # return most_common_string_u


#########################################################
#
# get_acceptable_dir_by_trend
#
#########################################################

def get_acceptable_dir_by_trend(trend):
    
    """Identifies the direction of the next movement
    
    Parameters
    ----------
    dir: string
        a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    
    Returns
    -------
    list
        a list of the acceptable directions
    """
    
    if trend == "N":
        # return ["W", "NW", "N", "NE", "E"]
        return ["NW", "N", "NE"]
    elif trend == "NE":
        # return ["NW", "N", "NE", "E", "SE"]
        return ["N", "NE", "E"]
    elif trend == "E":
        # return ["N", "NE", "E", "SE", "S"]
        return ["NE", "E", "SE"]
    elif trend == "SE":
        # return ["NE", "E", "SE", "S", "SW"]
        return ["E", "SE", "S"]
    elif trend == "S":
        # return ["E", "SE", "S", "SW", "W"]
        return ["SE", "S", "SW"]
    elif trend == "SW":
        # return ["SE", "S", "SW", "W", "NW"]
        return ["S", "SW", "W"]
    elif trend == "W":
        # return ["S", "SW", "W", "NW", "N"]
        return ["W", "SW", "S"]
    elif trend == "NW":
        # return ["SW", "W", "NW", "N", "NE"]
        return ["W", "NW", "N"]
    else:
        raise InvalidZonalDirectionException()
        sys.exit(101)


#########################################################
#
# get_acceptable_dir_by_trend
#
#########################################################

def get_acceptable_dir_by_complex_trend(trend):
    
    """Identifies the direction of the next movement
    
    Parameters
    ----------
    dir: string
        a string among "NE", "N", "NW", "E", "W", "SE", "S", "SW"
    
    Returns
    -------
    list
        a list of the acceptable directions
    """
    
    # get the two most-rated directions of the trend
    trendDirsFull = sorted(trend.items(),key=lambda x: x[1], reverse=True)[0:2]
    trendDirs = []
    trendDirs.append(trendDirsFull[0][0])
    if len(trendDirsFull) > 1:
        if trendDirsFull[0][1] - trendDirsFull[1][1] < 1:
            trendDirs.append(trendDirsFull[1][0])
    
    # initialise a list for allowed directions
    directions = []
    
    # loop over the two most-rated directions of the trend
    for trend in trendDirs:
        if trend == "N":
            for x in ["NW", "N", "NE"]:
                directions.append(x)
        elif trend == "NE":
            for x in ["N", "NE", "E"]:
                directions.append(x)
        elif trend == "E":
            for x in ["NE", "E", "SE"]:
                directions.append(x)
        elif trend == "SE":
            for x in ["E", "SE", "S"]:
                directions.append(x)
        elif trend == "S":
            for x in ["SE", "S", "SW"]:
                directions.append(x)
        elif trend == "SW":
            for x in ["S", "SW", "W"]:
                directions.append(x)
        elif trend == "W":
            for x in ["W", "SW", "S"]:
                directions.append(x)
        elif trend == "NW":
            for x in ["W", "NW", "N"]:
                directions.append(x)
        else:
            raise InvalidZonalDirectionException()
            sys.exit(101)
            
    return directions
