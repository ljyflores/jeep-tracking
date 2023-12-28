import numpy as np
import pandas as pd
import requests
import json
import random

from datetime import datetime
from haversine import haversine
from typing import List

TRACKER_CREDENTIALS = json.load(open("/home/airflow/gcs/data/tracker.json", "r"))
# TRACKER_CREDENTIALS = json.load(open("credentials/tracker.json", "r"))

### BIGQUERY FUNCTIONS ###
def insert_rows_bigquery(client, table_id, table, row_ids=None):
    rows = table.to_dict("records")
    errors = client.insert_rows_json(
        table_id, rows, row_ids=[None] * len(rows) if row_ids is None else row_ids
    )  # Make an API request.
    if errors == []:
        return "New rows have been added."
    else:
        return "Encountered errors while inserting rows: {}".format(errors)
    
def query_bigquery(client, QUERY):
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    output = [row for row in rows]
    return pd.DataFrame.from_dict([dict(row) for row in output])

def query_latest_etas(client):
    QUERY = (
        'SELECT agg.table.* FROM (SELECT stop_id, ARRAY_AGG(STRUCT(table) ORDER BY insertion_time DESC)[SAFE_OFFSET(0)] agg FROM `eco-folder-402813.jeep_etas.test` table GROUP BY stop_id)'
    )
    return query_bigquery(client, QUERY) 

def query_historical_table(client, table_id):
    QUERY = f"SELECT * FROM `{table_id}`"
    return query_bigquery(client, QUERY)

def postprocess_eta_table(records, jeep_information_dict):
    df_temp = pd.DataFrame(records)
    df_temp["jeep_plate_num_list"] = add_plate_numbers_to_df(df_temp["jeep_ids_list"], jeep_information_dict)
    df_temp["insertion_time"]      = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for col in [
        'jeep_ids_list', 
        'jeep_locations_list', 
        'jeep_arrival_times_list', 
        'jeep_plate_num_list', 
        'jeep_route_name_list'
        ]:
        df_temp[col] = df_temp[col].apply(lambda lst: ",".join([str(x) for x in lst]))
    df_temp["jeep_next_stop_name_list"] = df_temp["jeep_next_stop_name_list"].apply(lambda lst: ";".join([str(x) for x in lst]))

    return df_temp

### LOCATION AND PLATE NUMBER HELPER FUNCTIONS ###
def add_plate_numbers_to_df(jeep_id_col, jeep_information_dict):
    return jeep_id_col.apply(
        lambda lst: [jeep_information_dict[item]["plate_number"] for item in lst]
        )

def create_df_new_historical_addresses(
        name_lst: List[str], 
        coords_lst: List[tuple]
        ):
    temp = pd.DataFrame({
        "names": name_lst, 
        "lng": [c[0] for c in coords_lst],
        "lat": [c[1] for c in coords_lst]
        })
    return temp

def create_df_new_historical_etas(
        stop_id: str,
        location_list: List[tuple],
        eta_list: List[float]
        ):
    N = len(location_list)
    temp = pd.DataFrame({
        "stop_id": [stop_id]*N,
        "lng": [c[0] for c in location_list],
        "lat": [c[1] for c in location_list],
        "time": [datetime.now()]*N,
        "eta": eta_list
        })
    temp["time"] = temp["time"].dt.strftime('%Y-%m-%d %H:%M:%S')
    return temp

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

def query_gps(tracker_id: str):
    try:
        response = requests.post(
            url = "https://242.sinotrack.com/APP/AppJson.asp", 
            data = {
                "strAppID": TRACKER_CREDENTIALS["strAppID"],
                "strUser": tracker_id,
                "strRandom": TRACKER_CREDENTIALS["strRandom"],
                "nTimeStamp": TRACKER_CREDENTIALS["nTimeStamp"],
                "strSign": TRACKER_CREDENTIALS["strSign"],
                "strToken": TRACKER_CREDENTIALS["strToken"]
            }, 
            headers = {
                "POST": "/APP/AppJson.asp HTTP/1.1",
                "Host": "242.sinotrack.com",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Accept": "text/plain, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "http://sinotrackpro.com/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Content-Length": "220",
                "Origin": "http://sinotrackpro.com",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site"
            }
        ).json()
        return {
            "lng": float(response["m_arrRecord"][0][2]), 
            "lat": float(response["m_arrRecord"][0][3])
            }
    except:
        return {"lng": -999.9, "lat": -999.9}

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
        historical_jeep_times = np.array(pd.to_datetime(
            historical_stop["time"], 
            errors='coerce').dt.to_pydatetime())
        historical_jeep_etas  = np.array(historical_stop["eta"])

        for j, jeep_coord in enumerate(origin_coords):
            # Compute delta in location from the jeep to available historical data
            delta_locs = np.sum((jeep_coord-historical_jeep_locs)**2 + 0.001, axis=1)
            delta_locs  = np.exp(-1*np.abs(delta_locs))

            # Compute delta in times they were queried 
            helper = np.vectorize(lambda x: x.total_seconds())
            delta_times = helper(datetime.now() - historical_jeep_times) / 60
            delta_times = delta_times % 1440 # Don't take days into account
            delta_times = np.exp(-0.01*np.abs(0.001 + delta_times))
            
            # Use these as weights for the ETA
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
        tracker_mapping_dict: dict,
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
        tracker_mapping_dict (dict): Dictionary mapping Jepp ID to tracker number
        historical_geocoding_table (pd.DataFrame): Geocoding dataframe with 'names' and 'coords' columns
        historical_eta_table (pd.DataFrame): Historical ETA dataframe with 'stop_id', 'location', 'time', 'eta' columns
        use_mapbox (bool): True if using MapBox to query locations, False to use info from database

    Returns:
        _type_: _description_
    """
    # Get list of jeep IDs and coordinates
    jeep_ids = jeep_route_mapping_dict[route_name]
    jeep_locations = [query_gps(tracker_id=tracker_mapping_dict[jeep_id]) for jeep_id in jeep_ids]
    jeep_locations_arr = np.array([dict_to_tuple_coords(c) for c in jeep_locations])

    # Get list of stop IDs and coordinates
    stop_ids = route_stops_mapping_dict[route_name]
    stop_locations = [stop_coords_mapping_dict[stop_id] for stop_id in stop_ids]
    stop_locations_arr = np.array([dict_to_tuple_coords(c) for c in stop_locations])

    # Get list of stop names
    stop_names_list = [item["name"] for item in stop_locations]

    # Loop through the stops, and find the jeeps closest to them, their current locations,
    # and their arrival times
    stop_id_list, jeep_ids_list, jeep_locations_list, jeep_arrival_times_list, jeep_route_name_list, jeep_next_stop_name_list = [], [], [], [], [], []
    new_historical_geocoding_table = pd.DataFrame(columns=['names', 'lng', 'lat'])
    new_historical_eta_table = pd.DataFrame(columns=['stop_id', 'lng', 'lat', 'time', 'eta'])

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
            new_historical_geocoding_rows = create_df_new_historical_addresses(
                name_lst = jeep_found_locations, 
                coords_lst = jeep_found_coordinates
                )
            new_historical_eta_rows = create_df_new_historical_etas(
                stop_id = stop_id,
                location_list = [jeep_locations_arr[id] for id in closest_k_jeep_ids],
                eta_list = jeep_arrival_times
            )
            new_historical_geocoding_table = pd.concat([new_historical_geocoding_table, new_historical_geocoding_rows], ignore_index=True)
            new_historical_eta_table = pd.concat([new_historical_eta_table, new_historical_eta_rows], ignore_index=True)

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
            
        # Save the jeep IDs
        jeep_id_names = [jeep_ids[id] for id in closest_k_jeep_ids]
        
        # Save the jeep routes
        jeep_route_names = [route_name for _ in range(len(jeep_id_names))]
        jeep_next_stop_names = [",".join(stop_names_list) for _ in range(len(jeep_id_names))]

        stop_id_list.append(stop_id)
        jeep_ids_list.append(jeep_id_names)
        jeep_locations_list.append(jeep_final_locations)
        jeep_arrival_times_list.append(jeep_arrival_times)
        jeep_route_name_list.append(jeep_route_names)
        jeep_next_stop_name_list.append(jeep_next_stop_names)

    return {
        "stop_id": stop_id_list, 
        "stop_names": stop_names_list,
        "jeep_ids_list": jeep_ids_list,
        "jeep_locations_list": jeep_locations_list, 
        "jeep_arrival_times_list": jeep_arrival_times_list,
        "jeep_route_name_list": jeep_route_name_list,
        "jeep_next_stop_name_list": jeep_next_stop_name_list,
        "historical_geocoding_table": new_historical_geocoding_table,
        "historical_eta_table": new_historical_eta_table
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