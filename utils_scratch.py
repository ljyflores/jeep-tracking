import numpy as np
import requests

from haversine import haversine
from utils import compute_closest_pt

def get_address(lat, lng, GOOGLE_API_KEY):
    references = None
    reference_names = None
    acceptable_distance_km = 1

    # Find the closest point
    best_reference_idx = compute_closest_pt(np.array([lat, lng]), references)

    # If it's within an acceptable distance, return it
    if haversine(np.array([lat, lng]), references[best_reference_idx]) < acceptable_distance_km:
        return reference_names[best_reference_idx]
    
    # Otherwise, run geocoding
    else:
        address, address_google_maps_id = api_gmap_reverse_address(lat, lng, GOOGLE_API_KEY)
        if address is not None:
            save_address(lat, lng, address, address_google_maps_id)
        return address
    
def api_gmap_reverse_address(lat: float, lng: float, GOOGLE_API_KEY: str):
    """Return formatted address and Google place ID of given latitude and longitude

    Args:
        lat (float): Latitude (float)
        lng (float): Longitude (float)
        GOOGLE_API_KEY (str): Google API key

    Returns:
        (str, str): Tuple containing formatted address and Google place ID
    """

    r = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={GOOGLE_API_KEY}")

    backup_list = []
    for item in r.json()["results"]:
        if item["types"] in ["street_address", "premise", "establishment", "point_of_interest"]:
            return item["formatted_address"], item["place_id"]
        else:
            backup_list.append(item)
    if len(backup_list) > 0:
        return backup_list[0]["formatted_address"], backup_list[0]["place_id"]
    else:
        return None, None

def save_address(lat, lng, address, address_gmaps_id):
    pass

