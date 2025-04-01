import React, { useState, useEffect } from "react";
import { getRecommendations } from "../api";
import Map from "./Map";
import '../styles.css';

function RecommendationsList({ user }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isGoogleMapsLoaded, setIsGoogleMapsLoaded] = useState(false);

  useEffect(() => {
    // Check if Google Maps is loaded
    const checkGoogleMaps = () => {
      if (window.google && window.google.maps && window.google.maps.Geocoder) {
        setIsGoogleMapsLoaded(true);
        return true;
      }
      return false;
    };

    // If Google Maps is already loaded
    if (checkGoogleMaps()) {
      return;
    }

    // Wait for Google Maps to load
    const interval = setInterval(() => {
      if (checkGoogleMaps()) {
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const fetchRecommendations = async (coordinates) => {
    try {
      setLoading(true);
      setError(null);
      
      // Check if user is logged in
      if (!user || !user.id) {
        throw new Error('Please log in to get recommendations');
      }

      console.log('Fetching recommendations for coordinates:', coordinates);
      const response = await getRecommendations(user.id, coordinates);
      
      if (!response.data || !response.data.recommendations) {
        throw new Error('Invalid response format from API');
      }

      console.log('Received recommendations:', response.data.recommendations);
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError(error.message || 'Failed to fetch recommendations');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || !isGoogleMapsLoaded) return;

    try {
      setIsSearching(true);
      setError(null);
      
      // Use Geocoding service
      const geocoder = new window.google.maps.Geocoder();
      const result = await new Promise((resolve, reject) => {
        geocoder.geocode({ address: searchQuery }, (results, status) => {
          if (status === window.google.maps.GeocoderStatus.OK && results[0]) {
            resolve(results[0]);
          } else {
            reject(new Error(`Geocoding failed: ${status}`));
          }
        });
      });

      if (!result.geometry || !result.geometry.location) {
        throw new Error("Could not get location details");
      }

      const lat = result.geometry.location.lat();
      const lng = result.geometry.location.lng();
      
      console.log("Found location:", { lat, lng, address: result.formatted_address });
      
      setUserLocation({ lat, lng });
      await fetchRecommendations({ lat, lng });
    } catch (err) {
      console.error("Error searching location:", err);
      setError(err.message || "Failed to search location. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const getLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          console.log("Current location:", { latitude, longitude });
          
          setUserLocation({ lat: latitude, lng: longitude });
          await fetchRecommendations({ lat: latitude, lng: longitude });
        } catch (err) {
          console.error("Error processing current location:", err);
          setError("Failed to process your location. Please try searching for a location instead.");
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        setError("Failed to get your location. Please try searching for a location instead.");
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  // Set default location (San Francisco) if no location is selected
  useEffect(() => {
    if (isGoogleMapsLoaded && !userLocation) {
      const defaultLocation = { lat: 37.7749, lng: -122.4194 };
      setUserLocation(defaultLocation);
      fetchRecommendations(defaultLocation);
    }
  }, [isGoogleMapsLoaded]);

  return (
    <div className="recommendations-container">
      {!user ? (
        <div className="error-message">
          Please log in to get camping recommendations.
        </div>
      ) : (
        <>
          <div className="search-section">
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for a location..."
                className="search-input"
                disabled={loading}
              />
              <button 
                type="submit" 
                className="search-button"
                disabled={loading || isSearching}
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </form>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="map-section" style={{ height: 'calc(100vh - 200px)', marginTop: '20px' }}>
            <Map
              userLocation={userLocation}
              recommendations={recommendations}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default RecommendationsList; 