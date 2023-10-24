import numpy as np
import pandas as pd
import requests
import json
import random

from typing import List

def query_gps(jeep_id: str, use_random: bool):
    if use_random:
        return {"lng": random.uniform(121.02, 121.05), "lat": random.uniform(14.65, 14.70)}
    else:
        # return {"lng": None, "lat": None}
        raise NotImplementedError
    
def save_addresses(name_lst: List[str], coords_lst: List[tuple]):
    raise NotImplementedError

def query_historical_matrix(
    origin_coords: List[tuple], 
    destination_coords: List[tuple]
    ):
    raise NotImplementedError

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

def compute_closest_pt(coords: np.array, references: np.array):
    """Return the index of the reference with the closest distance from the coordinates

    Args:
        coords (np.array): Coordinate array of size (2,)
        references (np.array): Coordinate array of size (N,2)

    Returns index of reference with closest Euclidean dist

    """
    return np.argmin(np.sum((coords-references)**2, axis=1))

def query_route_updates(
    jeep_ids: List[str], 
    stop_ids: List[str],
    stop_coords_mapping_dict: dict,
    use_mapbox: bool = False,
    MAPBOX_API_KEY: str = None
    ):

    # Get list of jeep IDs and coordinates
    jeep_locations = [query_gps(jeep_id=jeep_id, use_random=True) for jeep_id in jeep_ids] # TODO: Fix this!

    # Get list of stop IDs and coordinates
    stop_locations = [stop_coords_mapping_dict[stop_id] for stop_id in stop_ids]

    # Map lng/lat dictionaries to tuples and pass into query function
    if use_mapbox: 
        assert MAPBOX_API_KEY is not None, print("MAPBOX API key cannot be none if querying")
        query_result = query_api_matrix(
            origin_coords = [dict_to_tuple_coords(coords) for coords in jeep_locations],
            destination_coords   = [dict_to_tuple_coords(coords) for coords in stop_locations], 
            MAPBOX_API_KEY = MAPBOX_API_KEY
            )
    else:
        query_result = query_historical_matrix(
            origin_coords = [dict_to_tuple_coords(coords) for coords in jeep_locations],
            destination_coords   = [dict_to_tuple_coords(coords) for coords in stop_locations]
        )

    # Unpack dictionary
    origin_names      = query_result["origin_names"]
    destination_names = query_result["destination_names"]
    origin_found_coords      = query_result["origin_found_coords"]
    destination_found_coords = query_result["destination_found_coords"]
    duration_matrix   = np.array(query_result["duration_matrix"])

    # Save address names and coordinates for future lookups
    # TODO: Implement
    # save_addresses(
    #     name_lst = origin_names+destination_names, 
    #     coords_lst = origin_found_coords+destination_found_coords
    #     )
    
    return pd.DataFrame({
        "stop_id": stop_ids,
        "list_of_jeeps": [jeep_ids]*len(stop_ids), # Gives all jeeps' distance from each stop
        "list_of_times": [duration_matrix[:,i] for i in range(duration_matrix.shape[1])] # Gives the time from jeep i to stop j
    })
