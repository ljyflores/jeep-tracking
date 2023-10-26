import numpy as np
import pandas as pd
import requests
import json
import random

from typing import List

def has_not_passed(stop_id: str, jeep_id: str):
    # TODO: Implement this
    return True

def query_gps(jeep_id: str, use_random: bool):
    if use_random:
        return {"lng": random.uniform(121.02, 121.05), "lat": random.uniform(14.65, 14.70)}
    else:
        # return {"lng": None, "lat": None}
        raise NotImplementedError
    
def save_addresses(name_lst: List[str], coords_lst: List[tuple]):
    pass # raise NotImplementedError

def query_historical_matrix(
    origin_coords: List[tuple], 
    destination_coords: List[tuple]
    ):
    raise NotImplementedError

def refine_location(
        found_coord: tuple, 
        found_location: str, 
        gps_location: tuple
        ):
    """Given the GPS location of a jeep and the map coordinate for which there is a 
    named address, figure out if we get a closer estimate of the jeep's location based
    on the coordinate-name pairs in our database. If a closer coordinate exists, return that 
    coordinate's location. Otherwise, return the one that MapBox found, given by 
    found_location.

    Args:
        found_coord (tuple): _description_
        found_location (str): _description_
        gps_location (tuple): _description_

    Returns:
        _type_: _description_
    """
    distance_to_found_coord = compute_closest_pts(
        coord = gps_location, 
        references = found_coord, 
        return_values = True
        )[1][0]
    db_idxs, db_distances = compute_closest_pts(
        coord = gps_location,
        references = 500*np.ones((200,2)), # db_coords, # TODO: Figure out
        return_values = True
    )
    if db_distances[0] < distance_to_found_coord:
        return "Insert better location from database here" # db[db_idxs[0]]["name"] # TODO: Figure out how to implement this
    else:
        return found_location
    
def dict_to_tuple_coords(d):
    return (d["lng"], d["lat"])

def read_json_path(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

def query_api_matrix(
    origin_coords: List[tuple], 
    destination_coords: List[tuple], 
    MAPBOX_API_KEY: str
    ):
    """Return a dictionary containing "origin_names", "destination_names", and
    len(origins) x len(dests) matrix of travel times in seconds from origins to 
    destinations

    Args:
        origin_coords (List[tuple]): List of coordinates passed in as (lng,lat) tuples
        destination_coords (List[tuple]): List of coordinates passed in as (lng,lat) tuples
        MAPBOX_API_KEY (str): Mapbox API key

    Returns:
        _type_: _description_
    """
    num_origins, num_dests = len(origin_coords), len(destination_coords)
    idx_origins, idx_dests = list(range(num_origins)), list(range(num_origins, num_origins+num_dests))

    coords_string      = ";".join([f"{coords[0]},{coords[1]}" for coords in origin_coords+destination_coords])
    idx_origins_string = ";".join([str(s) for s in idx_origins])
    idx_dests_string   = ";".join([str(s) for s in idx_dests])

    result = requests.get(
        f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coords_string}?annotations=duration&sources={idx_origins_string}&destinations={idx_dests_string}&access_token={MAPBOX_API_KEY}"
        ).json()
    
    origin_names      = [item["name"] for item in result["sources"]]
    destination_names = [item["name"] for item in result["destinations"]]

    origin_found_coords      = [item["location"] for item in result["sources"]]
    destination_found_coords = [item["location"] for item in result["destinations"]]

    duration_matrix   = result["durations"]
    
    return {
        "origin_names": origin_names,
        "destination_names": destination_names,
        "origin_found_coords": origin_found_coords,
        "destination_found_coords": destination_found_coords,
        "duration_matrix": duration_matrix
    }

def compute_closest_pts(coord: np.array, references: np.array, return_values: bool = False):
    """Return the index of the reference with the closest distance from the coordinates

    Args:
        coord (np.array): Coordinate array of size (2,)
        references (np.array): Coordinate array of size (N,2)
        return_values (bool): If True, return a second output containing a list of squared values

    Returns indices by increasing Euclidean dist

    """
    if len(references.shape) == 1:
        references = references.reshape(1,-1)

    distances = np.sum((coord-references)**2, axis=1)
    indices = np.argsort(distances)
    if return_values:
        return indices, distances[indices]
    else:
        return indices

def query_time_to_stops(
    jeep_coords: List[tuple], 
    stop_coords: List[tuple], 
    use_mapbox: bool = False,
    MAPBOX_API_KEY: str = None
    ):

    # Map lng/lat dictionaries to tuples and pass into query function
    if use_mapbox: 
        assert MAPBOX_API_KEY is not None, print("MAPBOX API key cannot be none if querying")
        query_result = query_api_matrix(
            origin_coords = jeep_coords,
            destination_coords = stop_coords, 
            MAPBOX_API_KEY = MAPBOX_API_KEY
            )
    else:
        query_result = query_historical_matrix(
            origin_coords = jeep_coords,
            destination_coords = stop_coords
        )

    # Unpack dictionary
    origin_names      = query_result["origin_names"]
    destination_names = query_result["destination_names"]
    origin_found_coords      = query_result["origin_found_coords"]
    destination_found_coords = query_result["destination_found_coords"]
    duration_matrix   = np.array(query_result["duration_matrix"])

    # Save address names and coordinates for future lookups
    save_addresses(
        name_lst = origin_names+destination_names, 
        coords_lst = origin_found_coords+destination_found_coords
        )
    
    return {
        "list_of_jeep_locs": origin_names,
        "list_of_jeep_coords": origin_found_coords,
        "duration_matrix": duration_matrix
    }

def find_k_closest_jeeps(stop_id: str, closest_jeep_ids: List[str], k: int):
    """Given a list of jeeps sorted by their proximity to a stop, return a list
    of the first k closest jeeps, while filtering out stops which the jeep has already
    passed

    Args:
        stop_id (str): _description_
        closest_jeep_ids (List[str]): _description_
        k (int): _description_

    Returns:
        _type_: _description_
    """
    output = []
    while len(output) < k and len(closest_jeep_ids) > 0:
        if has_not_passed(stop_id, closest_jeep_ids[0]):
            output.append(closest_jeep_ids[0])
        closest_jeep_ids = closest_jeep_ids[1:]
    return output

def query_route(
        route_name: str, 
        jeep_route_mapping_dict: dict, 
        route_stops_mapping_dict: dict, 
        stop_coords_mapping_dict: dict, 
        use_mapbox: bool,
        MAPBOX_API_KEY: str = None
        ):
    """For each stop in a given route, find the k closest jeeps to it, and return their current locations and
    time to arrivals

    Args:
        route_name (str): Route name (should exist in the mapping dictionary)
        jeep_route_mapping_dict (dict): Dictionary of the route name and the jeep IDs that travel that route (list)
        route_stops_mapping_dict (dict): Dictionary of the route name and the stop IDs on the route (list)
        stop_coords_mapping_dict (dict): Dictionary of the stop ID and its coordinate dictionary (dict)
        use_mapbox (bool): True if using MapBox to query locations, False to use info from database

    Returns:
        _type_: _description_
    """
    # Get list of jeep IDs and coordinates
    jeep_ids = jeep_route_mapping_dict[route_name]
    jeep_locations = [query_gps(jeep_id=jeep_id, use_random=True) for jeep_id in jeep_ids]
    jeep_locations_arr = np.array([dict_to_tuple_coords(c) for c in jeep_locations])

    # Get list of stop IDs and coordinates
    stop_ids = route_stops_mapping_dict[route_name]
    stop_locations = [stop_coords_mapping_dict[stop_id] for stop_id in stop_ids]
    stop_locations_arr = np.array([dict_to_tuple_coords(c) for c in stop_locations])

    # Loop through the stops, and find the jeeps closest to them, their current locations,
    # and their arrival times
    stop_id_list, jeep_ids_list, jeep_locations_list, jeep_arrival_times_list = [], [], [], []
    for i, stop_id in enumerate(stop_ids):
        # Find the jeep IDs which are currently closest to the stop
        closest_jeep_ids = compute_closest_pts(
            stop_locations_arr[i], jeep_locations_arr
            )
        # Get the top k closest jeeps, filtering out those which have already
        # passed the stop (i.e. if the jeep is close but already passed the stop,
        # we don't want it)
        closest_k_jeep_ids = find_k_closest_jeeps(stop_id, closest_jeep_ids, k=3)

        # Query the jeeps' current locations and arrival times
        query_time_result = query_time_to_stops(
            jeep_coords = [jeep_locations_arr[id] for id in closest_k_jeep_ids],
            stop_coords = [stop_locations_arr[i]],
            use_mapbox  = use_mapbox,
            MAPBOX_API_KEY = MAPBOX_API_KEY
        )

        # Save the current locations
        jeep_found_locations = query_time_result["list_of_jeep_locs"]
        jeep_found_coordinates = query_time_result["list_of_jeep_coords"]

        # If we queried the locations using MapBox, refine the names by looking 
        # up closer points from our database of coordinates to names
        print(jeep_found_coordinates)
        print(jeep_found_locations)
        print([jeep_locations_arr[id] for id in closest_k_jeep_ids])
        if use_mapbox:
            jeep_final_locations = [
                refine_location(np.array(found_coord), found_location, gps_location) for \
                (found_coord, found_location, gps_location) in \
                zip(
                    jeep_found_coordinates, 
                    jeep_found_locations, 
                    [jeep_locations_arr[id] for id in closest_k_jeep_ids]
                    )]
        # Otherwise, use the ones already from the database
        else:
            jeep_final_locations = jeep_found_locations

        # Save the arrival times
        duration_matrix = np.array(query_time_result["duration_matrix"])
        jeep_arrival_times = [duration_matrix[i,0] for i in range(len(closest_k_jeep_ids))]
        
        stop_id_list.append(stop_id)
        jeep_ids_list.append(closest_k_jeep_ids)
        jeep_locations_list.append(jeep_final_locations)
        jeep_arrival_times_list.append(jeep_arrival_times)
    
    return {
        "stop_id_list": stop_id_list, 
        "jeep_ids_list": jeep_ids_list,
        "jeep_locations_list": jeep_locations_list, 
        "jeep_arrival_times_list": jeep_arrival_times_list
    }