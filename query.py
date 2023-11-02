import argparse

from google.cloud import bigquery
from utils import (
    insert_rows_bigquery, 
    postprocess_eta_table,
    query_historical_table,
    query_route,
    read_json
    )

parser = argparse.ArgumentParser()
parser.add_argument("--use_mapbox", required=True, type=str)
parser.add_argument("--route_name", required=True, type=str)
args = parser.parse_args()

USE_MAPBOX = True if args.use_mapbox == "True" else False
ROUTE_NAME = args.route_name

BQ_API_KEY     = open("credentials/google_bq_key", "r").readlines()[0]
MAPBOX_API_KEY = open("credentials/mapbox_key", "r").readlines()[0]

BQ_PROJECT_NAME               = "eco-folder-402813"
BQ_CURRENT_ETAS_TABLE         = "eco-folder-402813.jeep_etas.test"
BQ_HISTORICAL_LOCATIONS_TABLE = "eco-folder-402813.historical_locations.test"
BQ_HISTORICAL_ETAS_TABLE      = "eco-folder-402813.historical_etas.test"

client = bigquery.Client(project=BQ_PROJECT_NAME)

# Load in the static dictionaries 
stop_coords_mapping_dict = read_json("data/stop_coords_mapping_dict.json")
jeep_route_mapping_dict  = read_json("data/jeep_route_mapping_dict.json")
jeep_information_dict    = read_json("data/jeep_information_dict.json")
route_stops_mapping_dict = read_json("data/route_stops_mapping_dict.json")

# Load in the BQ historical tables
historical_geocoding_table = query_historical_table(client, BQ_HISTORICAL_LOCATIONS_TABLE)
historical_eta_table       = query_historical_table(client, BQ_HISTORICAL_ETAS_TABLE)

temp = query_route(
    route_name = ROUTE_NAME,
    jeep_route_mapping_dict = jeep_route_mapping_dict, 
    route_stops_mapping_dict = route_stops_mapping_dict, 
    stop_coords_mapping_dict = stop_coords_mapping_dict, 
    historical_geocoding_table = historical_geocoding_table,
    historical_eta_table = historical_eta_table,
    use_mapbox = USE_MAPBOX,
    MAPBOX_API_KEY = MAPBOX_API_KEY
    )
# Retrieve tables and append to historical 
historical_geocoding_table = temp.pop("historical_geocoding_table")
historical_eta_table = temp.pop("historical_eta_table")

# If we used MapBox, update the historical tables
if USE_MAPBOX:
    insert_rows_bigquery(client, BQ_HISTORICAL_ETAS_TABLE, historical_eta_table, row_ids=None)
    insert_rows_bigquery(client, BQ_HISTORICAL_LOCATIONS_TABLE, historical_geocoding_table, row_ids=None)

# Update the table with the current ETAs for the stops
df_etas = postprocess_eta_table(temp, jeep_information_dict)
insert_rows_bigquery(client, BQ_CURRENT_ETAS_TABLE, df_etas, row_ids=None)

print("Success!")