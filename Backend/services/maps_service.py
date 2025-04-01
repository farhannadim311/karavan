# maps_service.py

import googlemaps
from flask import current_app
import time

def get_maps_client():
    api_key = ''
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY is not configured")
    return googlemaps.Client(key=api_key)

def get_nearby_places(lat, lon, radius=25000, place_type="campground"):
    """Get nearby places using the Google Places API."""
    gmaps = get_maps_client()
    
    print(f"Searching for {place_type} near {lat}, {lon}")
    
    # Search combinations for better results
    search_combinations = [
        ("campground", None),
        ("park", "camping"),
        ("park", "campground"),
        ("park", "tent camping"),
        ("park", "RV camping"),
        ("natural_feature", "camping"),
        ("point_of_interest", "camping"),
        ("park", None),  # Add general parks
        ("natural_feature", None),  # Add general natural features
        ("point_of_interest", None)  # Add general points of interest
    ]
    
    all_places = []
    seen_place_ids = set()  # To avoid duplicates
    
    for search_type, keyword in search_combinations:
        print(f"Trying search type: {search_type}, keyword: {keyword}")
        
        try:
            # First, get nearby places
            places_result = gmaps.places_nearby(
                location=(lat, lon),
                radius=radius,
                type=search_type,
                keyword=keyword
            )
            
            if not places_result.get("results"):
                print(f"No results found for {search_type}, {keyword}")
                continue
            
            # Process results and handle pagination
            while places_result.get("results"):
                for place in places_result["results"]:
                    place_id = place["place_id"]
                    
                    # Skip if we've already processed this place
                    if place_id in seen_place_ids:
                        continue
                    seen_place_ids.add(place_id)
                    
                    try:
                        # Get detailed information about the place
                        place_details = gmaps.place(
                            place_id,
                            fields=[
                                "name", 
                                "rating", 
                                "formatted_address", 
                                "geometry", 
                                "opening_hours", 
                                "photos", 
                                "website", 
                                "formatted_phone_number",
                                "types", 
                                "user_ratings_total", 
                                "reviews",
                                "amenity"
                            ]
                        )["result"]
                        
                        # Skip if not a camping-related place
                        if not any(camping_type in place_details.get("types", []) 
                                 for camping_type in ["campground", "park", "natural_feature", "point_of_interest"]):
                            continue
                        
                        # Get directions to calculate distance
                        directions = gmaps.directions(
                            origin=(lat, lon),
                            destination=place_id,
                            mode="driving"
                        )
                        
                        # Calculate distance from directions
                        distance = None
                        if directions and directions[0].get("legs"):
                            distance = directions[0]["legs"][0].get("distance", {}).get("value")
                        
                        # Create place object
                        place_obj = {
                            "name": place_details.get("name"),
                            "address": place_details.get("formatted_address"),
                            "location": {
                                "lat": place_details["geometry"]["location"]["lat"],
                                "lng": place_details["geometry"]["location"]["lng"]
                            },
                            "rating": place_details.get("rating"),
                            "user_ratings_total": place_details.get("user_ratings_total", 0),
                            "is_open": place_details.get("opening_hours", {}).get("open_now", True),
                            "photos": place_details.get("photos", []),
                            "website": place_details.get("website"),
                            "phone": place_details.get("formatted_phone_number"),
                            "types": place_details.get("types", []),
                            "distance": distance,
                            "directions": directions[0] if directions else None,
                            "amenities": place_details.get("amenity", [])
                        }
                        
                        all_places.append(place_obj)
                        print(f"Added place: {place_obj['name']} at {place_obj['address']}")
                        
                    except Exception as e:
                        print(f"Error processing place_id={place_id}: {e}")
                        continue
                
                # Handle pagination
                if "next_page_token" in places_result:
                    time.sleep(2)  # Wait before requesting next page
                    places_result = gmaps.places_nearby(
                        location=(lat, lon),
                        radius=radius,
                        type=search_type,
                        keyword=keyword,
                        page_token=places_result["next_page_token"]
                    )
                else:
                    break
                    
        except Exception as e:
            print(f"Error in search combination {search_type}, {keyword}: {e}")
            continue
    
    print(f"Found {len(all_places)} total places")
    return all_places

def get_hiking_trails(lat, lon, radius=25000):
    """Get nearby hiking trails using the Google Places API."""
    gmaps = get_maps_client()
    
    print(f"Searching for hiking trails near {lat}, {lon}")
    
    # Search combinations for better results
    search_combinations = [
        ("hiking_trail", None),
        ("park", "hiking"),
        ("natural_feature", "hiking"),
        ("park", "trail"),
        ("park", "hiking trail")
    ]
    
    all_trails = []
    
    for search_type, keyword in search_combinations:
        print(f"Trying search type: {search_type}, keyword: {keyword}")
        
        try:
            # First, get nearby places
            places_result = gmaps.places_nearby(
                location=(lat, lon),
                radius=radius,
                type=search_type,
                keyword=keyword
            )
            
            # Process results and handle pagination
            while places_result.get("results"):
                for place in places_result["results"]:
                    place_id = place["place_id"]
                    
                    try:
                        # Get detailed information about the place
                        place_details = gmaps.place(
                            place_id,
                            fields=[
                                "name", 
                                "rating", 
                                "formatted_address", 
                                "geometry", 
                                "opening_hours", 
                                "photos", 
                                "website", 
                                "formatted_phone_number",
                                "types", 
                                "user_ratings_total", 
                                "reviews"
                            ]
                        )["result"]
                        
                        # Get directions to calculate distance
                        directions = gmaps.directions(
                            origin=(lat, lon),
                            destination=place_id,
                            mode="driving"
                        )
                        
                        # Calculate distance from directions
                        distance = None
                        if directions and directions[0].get("legs"):
                            distance = directions[0]["legs"][0].get("distance", {}).get("value")
                        
                        # Create trail object
                        trail_obj = {
                            "name": place_details.get("name"),
                            "address": place_details.get("formatted_address"),
                            "location": {
                                "lat": place_details["geometry"]["location"]["lat"],
                                "lng": place_details["geometry"]["location"]["lng"]
                            },
                            "rating": place_details.get("rating"),
                            "user_ratings_total": place_details.get("user_ratings_total", 0),
                            "is_open": place_details.get("opening_hours", {}).get("open_now", True),
                            "photos": place_details.get("photos", []),
                            "website": place_details.get("website"),
                            "phone": place_details.get("formatted_phone_number"),
                            "types": place_details.get("types", []),
                            "distance": distance,
                            "directions": directions[0] if directions else None
                        }
                        
                        all_trails.append(trail_obj)
                        print(f"Added trail: {trail_obj['name']}")
                        
                    except Exception as e:
                        print(f"Error processing trail_id={place_id}: {e}")
                        continue
                
                # Handle pagination
                if "next_page_token" in places_result:
                    time.sleep(2)  # Wait before requesting next page
                    places_result = gmaps.places_nearby(
                        location=(lat, lon),
                        radius=radius,
                        type=search_type,
                        keyword=keyword,
                        page_token=places_result["next_page_token"]
                    )
                else:
                    break
                    
        except Exception as e:
            print(f"Error in search combination {search_type}, {keyword}: {e}")
            continue
    
    print(f"Found {len(all_trails)} total hiking trails")
    return all_trails

def get_location_details(address):
    """Get location details from an address using the Google Maps Geocoding API."""
    gmaps = get_maps_client()
    
    try:
        # Geocode the address
        geocode_result = gmaps.geocode(address)
        
        if not geocode_result:
            print(f"No results found for address: {address}")
            return None
            
        # Get the first result
        location = geocode_result[0]
        
        # Extract relevant information
        result = {
            "address": location["formatted_address"],
            "location": {
                "lat": location["geometry"]["location"]["lat"],
                "lng": location["geometry"]["location"]["lng"]
            },
            "place_id": location["place_id"],
            "types": location.get("types", []),
            "viewport": location["geometry"].get("viewport", {}),
            "bounds": location["geometry"].get("bounds", {})
        }
        
        print(f"Found location details for: {address}")
        return result
        
    except Exception as e:
        print(f"Error getting location details for {address}: {e}")
        return None
