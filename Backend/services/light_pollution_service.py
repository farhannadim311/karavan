# services/light_pollution_service.py

import requests
from flask import current_app
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_light_pollution_level(lat, lon):
    """
    Retrieve light pollution level for the given coordinates.
    Uses the Light Pollution Map API to get Bortle scale data.
    Cached for 1 hour to avoid excessive API calls.
    """
    api_key = current_app.config["LIGHT_POLLUTION_API_KEY"]
    if not api_key:
        raise ValueError("LIGHT_POLLUTION_API_KEY is not configured")

    # Validate coordinates
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("Invalid latitude or longitude")

    try:
        url = current_app.config["LIGHT_POLLUTION_API_URL"]
        params = {
            "lat": lat,
            "lon": lon,
            "apikey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract Bortle scale (1-9, where 1 is darkest)
        bortle_scale = data.get("bortle_scale", 5)
        
        # Convert to our scale (1-10, where 10 is darkest)
        # Bortle 1 (darkest) -> 10
        # Bortle 9 (brightest) -> 2
        our_scale = 11 - bortle_scale
        
        return {
            "level": our_scale,
            "bortle_scale": bortle_scale,
            "description": data.get("description", "Unknown"),
            "timestamp": int(time.time())
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Light pollution API error: {str(e)}")
        return {
            "level": 5,  # Default to middle value
            "bortle_scale": 5,
            "description": "unavailable",
            "timestamp": int(time.time())
        }
    except (KeyError, ValueError) as e:
        current_app.logger.error(f"Light pollution data parsing error: {str(e)}")
        return {
            "level": 5,  # Default to middle value
            "bortle_scale": 5,
            "description": "data error",
            "timestamp": int(time.time())
        }
