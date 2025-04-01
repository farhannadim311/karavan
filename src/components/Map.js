import React, { useEffect, useRef, useState } from 'react';

const Map = ({ userLocation, recommendations }) => {
  const mapRef = useRef(null);
  const [map, setMap] = useState(null);
  const [markers, setMarkers] = useState([]);

  useEffect(() => {
    // Load Google Maps script
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&libraries=places`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      // Initialize map after script loads
      const defaultCenter = userLocation || { lat: 37.7749, lng: -122.4194 }; // Default to San Francisco
      const mapInstance = new window.google.maps.Map(mapRef.current, {
        center: defaultCenter,
        zoom: 12,
        mapId: process.env.REACT_APP_GOOGLE_MAPS_ID
      });
      setMap(mapInstance);
    };

    return () => {
      // Cleanup
      document.head.removeChild(script);
      if (map) {
        window.google.maps.event.clearInstanceListeners(map);
      }
    };
  }, []);

  // Update map center when user location changes
  useEffect(() => {
    if (map && userLocation) {
      map.setCenter(userLocation);
    }
  }, [map, userLocation]);

  // Update markers when recommendations change
  useEffect(() => {
    if (!map || !recommendations) return;

    // Clear existing markers
    markers.forEach(marker => marker.setMap(null));
    const newMarkers = [];

    // Add user location marker
    if (userLocation) {
      const userMarker = new window.google.maps.Marker({
        position: userLocation,
        map: map,
        title: 'Your Location',
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: '#4285F4',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 2
        }
      });
      newMarkers.push(userMarker);
    }

    // Add recommendation markers
    recommendations.forEach(rec => {
      const marker = new window.google.maps.Marker({
        position: rec.location,
        map: map,
        title: rec.name,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: '#FFA500',
          fillOpacity: 0.8,
          strokeColor: '#ffffff',
          strokeWeight: 2
        }
      });
      newMarkers.push(marker);
    });

    setMarkers(newMarkers);

    // Fit bounds to show all markers
    if (newMarkers.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();
      newMarkers.forEach(marker => bounds.extend(marker.getPosition()));
      map.fitBounds(bounds);
    }

    return () => {
      newMarkers.forEach(marker => marker.setMap(null));
    };
  }, [map, recommendations, userLocation]);

  return (
    <div 
      ref={mapRef} 
      style={{ 
        width: '100%', 
        height: '100%', 
        minHeight: '500px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }} 
    />
  );
};

export default Map; 