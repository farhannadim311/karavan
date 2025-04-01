// src/components/RecommendationsList.js
import React, { useState } from "react";
import { getRecommendations } from "../api";

function RecommendationsList({ user }) {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [recs, setRecs] = useState(null);

  const fetchRecommendations = async () => {
    try {
      const res = await getRecommendations(lat, lon, user.id, {});
      setRecs(res.data);
    } catch (err) {
      console.error(err);
      alert("Error fetching recommendations");
    }
  };

  const useMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
      });
    } else {
      alert("Geolocation is not supported by this browser.");
    }
  };

  return (
    <div>
      <h2>Find Campsites for Stargazing</h2>
      <div>
        <button onClick={useMyLocation}>Use My Current Location</button>
      </div>
      <div>
        <label>Latitude: </label>
        <input
          value={lat}
          onChange={(e) => setLat(e.target.value)}
          placeholder="e.g. 37.7749"
        />
      </div>
      <div>
        <label>Longitude: </label>
        <input
          value={lon}
          onChange={(e) => setLon(e.target.value)}
          placeholder="e.g. -122.4194"
        />
      </div>
      <button onClick={fetchRecommendations}>Get Recommendations</button>

      {recs && (
        <div>
          <h3>AI Summary:</h3>
          <p>{recs.ai_summary}</p>

          <h3>Ranked Recommendations:</h3>
          <ul>
            {recs.results.map((r, i) => (
              <li key={i}>
                <strong>{r.name}</strong> - Score: {r.score.toFixed(2)} <br/>
                Distance: {r.distance.toFixed(2)} km<br/>
                Light Pollution Level: {r.light_pollution_level}<br/>
                Weather: {r.weather.description}, {r.weather.temp}°C<br/>
                Availability: {r.availability ? "Yes" : "No"}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default RecommendationsList;
