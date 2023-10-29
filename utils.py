import numpy as np
import pandas as pd
import requests
import json
import random

from datetime import datetime
from haversine import haversine
from typing import List

### LOCATION AND PLATE NUMBER HELPER FUNCTIONS ###
def add_plate_numbers_to_df(jeep_id_col, jeep_information_dict):
    return jeep_id_col.apply(
        lambda lst: [jeep_information_dict[item]["plate_number"] for item in lst]
        )

def save_addresses(
        historical_geocoding_table: pd.DataFrame, 
        name_lst: List[str], 
        coords_lst: List[tuple]
        ):
    temp = pd.DataFrame({
        "names": name_lst, 
        "lat": [c[0] for c in coords_lst], 
        "lng": [c[1] for c in coords_lst]
        })
    historical_geocoding_table = pd.concat([historical_geocoding_table, temp], ignore_index=True)
    return historical_geocoding_table

def save_etas(
        historical_eta_table: pd.DataFrame,
        stop_id: str,
        location_list: List[tuple],
        eta_list: List[float]
        ):
    N = len(location_list)
    temp = pd.DataFrame({
        "stop_id": [stop_id]*N,
        "lat": [c[0] for c in location_list],
        "lng": [c[1] for c in location_list],
        "time": [datetime.now()]*N,
        "eta": eta_list
        })
    historical_eta_table = pd.concat([historical_eta_table, temp], ignore_index=True)
    return historical_eta_table

def refine_location(
        found_coord: tuple, 
        found_location: str, 
        gps_location: tuple,
        historical_geocoding_table: pd.DataFrame
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
        historical_geocoding_table (pd.DataFrame): _description_

    Returns:
        _type_: _description_
    """

    acceptable_distance_km = 0.010
    print(gps_location, found_coord)
    if haversine(
        (gps_location[1], gps_location[0]), 
        (found_coord[1], found_coord[0])
        ) < acceptable_distance_km:
        return found_location
    else:
        return query_historical_names(historical_geocoding_table, [gps_location])[0]
    
def query_historical_names(
        historical_table: pd.DataFrame, 
        coordinates: List[tuple]
        ):
    historical_table_coordinates = np.array([historical_table.lng, historical_table.lat]).T
    historical_table_names = np.array(historical_table.names)
    matched_idxs = map(
        lambda c: compute_closest_pts(
            coord=c, 
            references=historical_table_coordinates
            )[0], 
            coordinates)
    return [historical_table_names[idx] for idx in matched_idxs]

### TRAVEL TIME HELPER FUNCTIONS ###
def dict_to_tuple_coords(d):
    return (d["lng"], d["lat"])

# TODO: Implement this
def has_not_passed(stop_id: str, jeep_id: str):
    return True

# TODO: Get API working
def query_gps(jeep_id: str, use_random: bool):
    if use_random:
        return {"lng": random.uniform(121.02, 121.05), "lat": random.uniform(14.65, 14.70)}
    else:
        # return {"lng": None, "lat": None}
        raise NotImplementedError

def query_historical_matrix(
        historical_table: pd.DataFrame,
        origin_coords: List[tuple], # Jeepney coordinates
        stop_ids: List[str] # Stop IDs
    ):

    duration_matrix = -1*np.ones((len(origin_coords), len(stop_ids)))
    for i, stop_id in enumerate(stop_ids):
        historical_stop = historical_table.loc[historical_table["stop_id"] == stop_id]
        
        if len(historical_stop) == 0:
            continue

        historical_jeep_locs  = np.array([historical_stop["lng"], historical_stop["lat"]]).T
        historical_jeep_times = np.array(historical_stop["time"].dt.to_pydatetime())
        historical_jeep_etas  = np.array(historical_stop["eta"])

        for j, jeep_coord in enumerate(origin_coords):
            # Compute delta in location from the jeep to available historical data
            # and the times they were queried – to use as weights for the ETA
            delta_locs  = np.exp(-1*np.abs(np.sum((jeep_coord-historical_jeep_locs)**2, axis=1)))
            helper = np.vectorize(lambda x: x.total_seconds())
            delta_times = datetime.now()-historical_jeep_times
            delta_times = np.exp(-0.01*np.abs(helper(delta_times)/60))
            weights = delta_locs * delta_times
            # Normalize
            weights = weights/np.sum(weights)
            # Use weights to take weighted average of ETA
            duration_matrix[j,i] = np.sum(historical_jeep_etas * weights)

    return duration_matrix

def query_api_matrix(
    origin_coords: List[tuple], 
    destination_coords: List[tuple], 
    # historical_geocoding_table: pd.DataFrame,
    # historical_eta_table: pd.DataFrame,
    MAPBOX_API_KEY: str
    ):
    """Return a dictionary containing "origin_names", "destination_names", and
    len(origins) x len(dests) matrix of travel times in seconds from origins to 
    destinations

    Args:
        origin_coords (List[tuple]): List of coordinates passed in as (lng,lat) tuples
        destination_coords (List[tuple]): List of coordinates passed in as (lng,lat) tuples
        # historical_geocoding_table (pd.DataFrame): Geocoding dataframe with 'names' and 'coords' columns
        # historical_eta_table (pd.DataFrame): Historical ETA dataframe with 'stop_id', 'location', 'time', 'eta' columns
        MAPBOX_API_KEY (str): Mapbox API key

    Returns:
        _type_: _description_
    """
    num_origins, num_dests = len(origin_coords), len(destination_coords)
    idx_origins, idx_dests = list(range(num_origins)), list(range(num_origins, num_origins+num_dests))

    coords_string      = ";".join([f"{coords[0]},{coords[1]}" for coords in origin_coords+destination_coords])
    idx_origins_string = ";".join([str(s) for s in idx_origins])
    idx_dests_string   = ";".join([str(s) for s in idx_dests])
    print(coords_string)

    result = requests.get(
        f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coords_string}?annotations=duration&sources={idx_origins_string}&destinations={idx_dests_string}&access_token={MAPBOX_API_KEY}"
        ).json()
    
    origin_names        = [item["name"] for item in result["sources"]]
    origin_found_coords = [item["location"] for item in result["sources"]]
    duration_matrix     = np.array(result["durations"])
    # destination_names = [item["name"] for item in result["destinations"]]
    # destination_found_coords = [item["location"] for item in result["destinations"]]
        
    return {
        "list_of_jeep_locs": origin_names,
        "list_of_jeep_coords": origin_found_coords,
        "duration_matrix": duration_matrix
    }

def query_route(
        route_name: str, 
        jeep_route_mapping_dict: dict, 
        route_stops_mapping_dict: dict, 
        stop_coords_mapping_dict: dict, 
        historical_geocoding_table: pd.DataFrame,
        historical_eta_table: pd.DataFrame,
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
        historical_geocoding_table (pd.DataFrame): Geocoding dataframe with 'names' and 'coords' columns
        historical_eta_table (pd.DataFrame): Historical ETA dataframe with 'stop_id', 'location', 'time', 'eta' columns
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

    print(jeep_locations_arr)
    print(stop_locations_arr)

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
        if use_mapbox:
            # Query the matrix, and current jeep locations + coordinates
            query_result = query_api_matrix(
                origin_coords = [jeep_locations_arr[id] for id in closest_k_jeep_ids],
                destination_coords = [stop_locations_arr[i]], 
                MAPBOX_API_KEY = MAPBOX_API_KEY
                )
            
            # Unpack results
            jeep_found_locations   = query_result["list_of_jeep_locs"]
            jeep_found_coordinates = query_result["list_of_jeep_coords"]
            duration_matrix        = query_result["duration_matrix"]
            
            # Save the arrival times        
            jeep_arrival_times = [duration_matrix[i,0] for i in range(len(closest_k_jeep_ids))]

            # Save address names and coordinates for future lookups
            historical_geocoding_table = save_addresses(
                historical_geocoding_table = historical_geocoding_table,
                name_lst = jeep_found_locations, 
                coords_lst = jeep_found_coordinates
                )
            historical_eta_table = save_etas(
                historical_eta_table = historical_eta_table,
                stop_id = stop_id,
                location_list = [jeep_locations_arr[id] for id in closest_k_jeep_ids],
                eta_list = jeep_arrival_times
            )

            # If we queried the locations using MapBox, refine the names by looking 
            # up closer points from our database of coordinates to names
            jeep_final_locations = [
                refine_location(
                    np.array(found_coord), 
                    found_location, 
                    gps_location,
                    historical_geocoding_table
                    ) for \
                (found_coord, found_location, gps_location) in \
                zip(
                    jeep_found_coordinates, 
                    jeep_found_locations, 
                    [jeep_locations_arr[id] for id in closest_k_jeep_ids]
                    )]
            
        else:
            jeep_coords = [jeep_locations_arr[id] for id in closest_k_jeep_ids]
            duration_matrix = query_historical_matrix(
                historical_table = historical_eta_table,
                origin_coords = jeep_coords,
                stop_ids = [stop_id]
            )
            jeep_final_locations = query_historical_names(
                historical_table = historical_geocoding_table,
                coordinates = jeep_coords
            )
            # Save the arrival times        
            jeep_arrival_times = [duration_matrix[i,0] for i in range(len(closest_k_jeep_ids))]

            #
        # Save the jeep IDs
        jeep_id_names = [jeep_ids[id] for id in closest_k_jeep_ids]

        stop_id_list.append(stop_id)
        jeep_ids_list.append(jeep_id_names)
        jeep_locations_list.append(jeep_final_locations)
        jeep_arrival_times_list.append(jeep_arrival_times)
    
    return {
        "stop_id_list": stop_id_list, 
        "jeep_ids_list": jeep_ids_list,
        "jeep_locations_list": jeep_locations_list, 
        "jeep_arrival_times_list": jeep_arrival_times_list,
        "historical_geocoding_table": historical_geocoding_table,
        "historical_eta_table": historical_eta_table
    }

### JSON UTILITIES ###
def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

def save_json(dictionary, path):
    with open(path, "w") as outfile:
        json.dump(dictionary, outfile, indent=4)

### COMPUTE HELPER FUNCTIONS ###
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