// src/components/Profile.js
import React, { useState } from "react";
import { updatePreferences } from "../api";

function Profile({ user }) {
  const [fishing, setFishing] = useState(user.prefers_fishing);
  const [hiking, setHiking] = useState(user.prefers_hiking);
  const [solitude, setSolitude] = useState(user.prefers_solitude);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const savePreferences = async () => {
    setIsLoading(true);
    setMessage("");
    try {
      const res = await updatePreferences(user.id, {
        prefers_fishing: fishing,
        prefers_hiking: hiking,
        prefers_solitude: solitude
      });
      setMessage("Preferences updated successfully!");
    } catch (err) {
      setMessage("Error updating preferences. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h2>Your Profile</h2>
        <p className="user-email">{user.email}</p>
      </div>

      <div className="preferences-section">
        <h3>Camping Preferences</h3>
        <div className="preferences-grid">
          <div className="preference-item">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={fishing}
                onChange={(e) => setFishing(e.target.checked)}
              />
              <span className="checkbox-text">Fishing</span>
            </label>
          </div>
          <div className="preference-item">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={hiking}
                onChange={(e) => setHiking(e.target.checked)}
              />
              <span className="checkbox-text">Hiking</span>
            </label>
          </div>
          <div className="preference-item">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={solitude}
                onChange={(e) => setSolitude(e.target.checked)}
              />
              <span className="checkbox-text">Solitude</span>
            </label>
          </div>
        </div>
      </div>

      <div className="profile-actions">
        <button 
          onClick={savePreferences} 
          disabled={isLoading}
          className="save-button"
        >
          {isLoading ? "Saving..." : "Save Preferences"}
        </button>
        {message && (
          <div className={`message ${message.includes("Error") ? "error" : "success"}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;
