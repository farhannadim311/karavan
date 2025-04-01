# recommendation.py
# recommendation.py

import math
import time
from services.weather_service import get_weather
from services.maps_service import get_nearby_places, get_hiking_trails
from services.gemini_service import get_ai_recommendation

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLng = math.radians(lng2 - lng1)
    a = (math.sin(dLat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLng/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def estimate_light_pollution(weather_data):
    """Estimate light pollution level based on weather conditions"""
    # Base level (0-10, where 10 is best for stargazing)
    level = 5
    
    # Cloud coverage (most important factor for stargazing)
    clouds = weather_data.get("clouds")
    if clouds is not None:
        if clouds < 10:  # Almost clear sky
            level += 3
        elif clouds < 20:  # Mostly clear
            level += 2
        elif clouds < 30:  # Partly cloudy
            level += 1
        elif clouds > 90:  # Overcast
            level -= 3
        elif clouds > 70:  # Mostly cloudy
            level -= 2
        elif clouds > 50:  # Partly cloudy
            level -= 1
            
    # Visibility (affects atmospheric clarity)
    visibility = weather_data.get("visibility")
    if visibility is not None:
        if visibility > 20000:  # Excellent visibility
            level += 2
        elif visibility > 10000:  # Good visibility
            level += 1
        elif visibility < 3000:  # Poor visibility
            level -= 2
        elif visibility < 5000:  # Fair visibility
            level -= 1
            
    # Temperature (affects atmospheric stability)
    temp = weather_data.get("temp")
    if temp is not None:
        if 10 <= temp <= 25:  # Ideal temperature range
            level += 1
        elif temp < 0 or temp > 30:  # Extreme temperatures
            level -= 1
            
    # Precipitation (worst for stargazing)
    if weather_data.get("rain"):
        level -= 3
    elif weather_data.get("snow"):
        level -= 2
        
    # Wind speed (affects atmospheric stability)
    wind = weather_data.get("wind_speed")
    if wind is not None:
        if wind > 30:  # Strong winds
            level -= 2
        elif wind > 20:  # Moderate winds
            level -= 1
            
    # Humidity (affects atmospheric clarity)
    humidity = weather_data.get("humidity")
    if humidity is not None:
        if humidity > 90:  # Very humid
            level -= 2
        elif humidity > 80:  # Humid
            level -= 1
            
    # Moon phase (if available)
    if "moon_phase" in weather_data:
        moon = weather_data["moon_phase"]
        if moon < 0.2:  # New moon (best)
            level += 2
        elif moon < 0.4:  # Waxing crescent
            level += 1
        elif moon > 0.8:  # Full moon (brightest)
            level -= 2
        elif moon > 0.6:  # Waning gibbous
            level -= 1
        
    # Ensure level stays within 0-10 range
    return max(0, min(10, level))

def recommend_campsites(user_lat, user_lng, user_preferences):
    """
    1) Fetch nearby campsites and hiking trails using Google Maps
    2) Get weather data for each location
    3) Filter and score based on user preferences
    4) Generate AI recommendations
    """
    try:
        print(f"Searching for camping spots near coordinates: {user_lat}, {user_lng}")
        
        # 1) Get potential locations (25 km by default)
        campsites = get_nearby_places(user_lat, user_lng, radius=25000)
        print(f"Found {len(campsites)} potential camping spots.")
        
        if not campsites:
            print("No camping spots found, returning empty recommendations.")
            return {
                "recommendations": [],
                "ai_summary": {
                    "text": (
                        "No camping spots found in your area. "
                        "Try searching in a different location or expanding your search radius."
                    ),
                    "timestamp": int(time.time())
                }
            }
            
        # 2) Fetch hiking trails (only if user prefers hiking)
        hiking_trails = []
        if user_preferences.get("prefers_hiking"):
            hiking_trails = get_hiking_trails(user_lat, user_lng, radius=25000)
            print(f"Found {len(hiking_trails)} hiking trails.")
        
        results = []
        # Process only the first 10 campsites to improve performance
        for site in campsites[:10]:
            try:
                print(f"Processing location: {site.get('name', 'Unnamed')}")
                
                # Get weather data
                lat_site = site["location"]["lat"]
                lng_site = site["location"]["lng"]
                weather = get_weather(lat_site, lng_site)
                print(f"Weather for {site['name']}: {weather.get('description')}")

                # Estimate light pollution
                light_pollution = {
                    "level": estimate_light_pollution(weather),
                    "description": "Estimated based on weather conditions"
                }
                
                # Handle distance (site["distance"] is in meters, might be None)
                raw_distance = site.get("distance")
                if raw_distance is not None:
                    distance = raw_distance / 1000  # convert to km
                else:
                    # Calculate distance using haversine formula if directions not available
                    distance = haversine_distance(user_lat, user_lng, lat_site, lng_site)
                print(f"Distance to {site['name']}: {distance:.2f}km")
                
                # Base score
                base_score = 10
                
                # Weather factors
                if weather["temp"] and 15 <= weather["temp"] <= 25:  # Ideal temperature range
                    base_score += 2
                if weather["clouds"] is not None and weather["clouds"] < 30:  # Clear-ish skies
                    base_score += 2
                if not weather["rain"]:
                    base_score += 1
                    
                # Light pollution
                if light_pollution["level"] >= 8:  # Excellent
                    base_score += 3
                elif light_pollution["level"] >= 6:  # Good
                    base_score += 2
                    
                # Distance penalty (less penalty for closer places)
                if distance < 5:  # Within 5km
                    base_score += 2
                elif distance < 10:  # Within 10km
                    base_score += 1
                else:
                    base_score -= (distance / 20)  # Less penalty for longer distances
                
                # User preference factors
                if user_preferences.get("prefers_fishing") and "fishing" in site.get("amenities", []):
                    base_score += 2
                
                if user_preferences.get("prefers_hiking") and hiking_trails:
                    # Check for nearby hiking trails
                    nearby_trails = [
                        t for t in hiking_trails
                        if haversine_distance(
                            lat_site, lng_site,
                            t["location"]["lat"], t["location"]["lng"]
                        ) < 5  # within 5 km
                    ]
                    if nearby_trails:
                        base_score += 2
                
                if user_preferences.get("prefers_solitude") and not site.get("is_open", True):
                    base_score += 1
                
                # Additional factors
                if site.get("rating", 0) >= 4.5:  # Highly rated places
                    base_score += 2
                elif site.get("rating", 0) >= 4.0:  # Well-rated places
                    base_score += 1
                
                if site.get("user_ratings_total", 0) > 100:  # Popular places
                    base_score += 1
                
                print(f"Final score for {site['name']}: {base_score:.2f}")
                
                results.append({
                    "name": site["name"],
                    "address": site["address"],
                    "location": site["location"],
                    "distance": distance,
                    "weather": weather,
                    "light_pollution": light_pollution,
                    "rating": site.get("rating", 0),
                    "is_open": site.get("is_open", True),
                    "photos": site.get("photos", []),
                    "website": site.get("website"),
                    "phone": site.get("phone"),
                    "directions": site.get("directions"),
                    "score": base_score,
                    "types": site.get("types", []),
                    "user_ratings_total": site.get("user_ratings_total", 0),
                    "amenities": site.get("amenities", [])
                })
            except Exception as e:
                print(f"Error processing campsite '{site.get('name', 'unknown')}': {str(e)}")
                continue
        
        if not results:
            print("No valid results after processing. Possibly all had errors or distance=0.")
            return {
                "recommendations": [],
                "ai_summary": {
                    "text": "Unable to process camping spots in your area. Please try again later.",
                    "timestamp": int(time.time())
                }
            }
        
        # Sort by score and take top 3
        results.sort(key=lambda x: x["score"], reverse=True)
        top_spots = results[:3]
        print(f"Successfully processed {len(top_spots)} camping spots.")
        
        # Generate a simple summary
        summary = f"Found {len(top_spots)} camping spots near your location. "
        if top_spots:
            summary += f"The best option is {top_spots[0]['name']} with a score of {top_spots[0]['score']:.1f}. "
            summary += f"It's {top_spots[0]['distance']:.1f}km away with {top_spots[0]['light_pollution']['level']}/10 light pollution."
        
        return {
            "recommendations": top_spots,
            "ai_summary": {
                "text": summary,
                "timestamp": int(time.time())
            }
        }
        
    except Exception as e:
        print(f"Error in recommend_campsites: {e}")
        return {
            "recommendations": [],
            "ai_summary": {
                "text": "An error occurred while generating recommendations. Please try again.",
                "timestamp": int(time.time())
            }
        }
