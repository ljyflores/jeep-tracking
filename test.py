from utils import read_json, query_route, add_plate_numbers_to_df
import googlemaps
import pandas as pd
from datetime import datetime

# GOOGLE_API_KEY = open('google_maps_key', 'r').readlines()[0]
# gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

BQ_API_KEY = open('google_bq_key', 'r').readlines()[0]
MAPBOX_API_KEY = open('mapbox_key', 'r').readlines()[0]


stop_coords_mapping_dict = read_json("data/stop_coords_mapping_dict.json")
jeep_route_mapping_dict = read_json("data/jeep_route_mapping_dict.json")
jeep_information_dict = read_json("data/jeep_information_dict.json")
route_stops_mapping_dict = read_json("data/route_stops_mapping_dict.json")

historical_geocoding_table = pd.DataFrame({
    "names": ["A", "B", "C"],
    "lng": [121.5, 121.25, 121.0],
    "lat": [14.5, 14.25, 14.0]
})

historical_eta_table = pd.DataFrame({
    "stop_id": ["AL1", "AL1", "AL1", "AL2", "AL2"], 
    "lng": [121.98, 121.25, 121.66, 121.23, 121.95], 
    "lat": [14.23, 14.74, 14.63, 14.33, 14.04],
    "time": [datetime.now()]*5, 
    "eta": [5.52, 7.84, 2.25, 11.54, 4.25]
})

temp = query_route(
    route_name = "aurora_loop",
    jeep_route_mapping_dict = jeep_route_mapping_dict, 
    route_stops_mapping_dict = route_stops_mapping_dict, 
    stop_coords_mapping_dict = stop_coords_mapping_dict, 
    historical_geocoding_table = historical_geocoding_table,
    historical_eta_table = historical_eta_table,
    use_mapbox = False,
    MAPBOX_API_KEY = MAPBOX_API_KEY
    )
historical_geocoding_table = temp.pop("historical_geocoding_table")
historical_eta_table = temp.pop("historical_eta_table")