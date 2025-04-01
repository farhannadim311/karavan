 

# weather_service.py

import requests
from flask import current_app
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_weather(lat, lon):
    """
    Fetch weather data from OpenWeatherMap API.
    Cached for 1 hour to avoid excessive API calls.
    """
    api_key = current_app.config["WEATHER_API_KEY"]
    if not api_key:
        raise ValueError("WEATHER_API_KEY is not configured")

    # Validate coordinates
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("Invalid latitude or longitude")

    try:
        url = current_app.config["WEATHER_API_URL"]
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Basic weather info
        weather = {
            "temp": data.get("main", {}).get("temp"),
            "description": data.get("weather", [{}])[0].get("description", "unknown"),
            "clouds": data.get("clouds", {}).get("all"),
            "rain": bool(data.get("rain")),     # or data.get("rain", {}).get("1h", 0) if you want numeric
            "snow": bool(data.get("snow")),     # similarly if you want numeric
            "humidity": data.get("main", {}).get("humidity"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "visibility": data.get("visibility"),
            "timestamp": int(time.time())
        }
        
        return weather
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Weather API error: {str(e)}")
        return {
            "temp": None,
            "description": "unavailable",
            "clouds": None,
            "rain": False,
            "snow": False,
            "humidity": None,
            "wind_speed": None,
            "visibility": None,
            "timestamp": int(time.time())
        }
    except (KeyError, ValueError) as e:
        current_app.logger.error(f"Weather data parsing error: {str(e)}")
        return {
            "temp": None,
            "description": "data error",
            "clouds": None,
            "rain": False,
            "snow": False,
            "humidity": None,
            "wind_speed": None,
            "visibility": None,
            "timestamp": int(time.time())
        }
