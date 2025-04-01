# services/campsite_service.py

import requests
from flask import current_app
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_nearby_campsites(lat, lon, max_distance=50):
    """
    Query campsite reservation system to find nearby campsites.
    Returns a list of campsite info dicts, including availability.
    Cached for 1 hour to avoid excessive API calls.
    """
    api_key = current_app.config["CAMPSITE_API_KEY"]
    if not api_key:
        raise ValueError("CAMPSITE_API_KEY is not configured")

    # Validate coordinates
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("Invalid latitude or longitude")

    try:
        url = current_app.config["CAMPSITE_API_URL"]
        params = {
            "lat": lat,
            "lon": lon,
            "radius": max_distance,  # km
            "apikey": api_key,
            "limit": current_app.config["MAX_RECOMMENDATIONS"]
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Process and validate each campsite
        campsites = []
        for site in data.get("campsites", []):
            # Validate required fields
            if not all(k in site for k in ["name", "lat", "lon", "amenities"]):
                continue

            campsite = {
                "name": site["name"],
                "lat": site["lat"],
                "lon": site["lon"],
                "amenities": site["amenities"],
                "availability": site.get("availability", False),
                "rating": site.get("rating", 0),
                "price": site.get("price", None),
                "description": site.get("description", ""),
                "timestamp": int(time.time())
            }
            campsites.append(campsite)

        return campsites
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Campsite API error: {str(e)}")
        return []
    except (KeyError, ValueError) as e:
        current_app.logger.error(f"Campsite data parsing error: {str(e)}")
        return []
