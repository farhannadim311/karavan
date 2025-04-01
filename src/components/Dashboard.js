// src/components/Dashboard.js
import React, { useState } from "react";
import RecommendationsList from "./RecommendationsList";
import Profile from "./Profile";

function Dashboard({ user, setUser }) {
  const [view, setView] = useState("recommendations");

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-brand">Camping & Stargazing</div>
        <div className="nav-links">
          <button 
            className={`nav-button ${view === "recommendations" ? "active" : ""}`}
            onClick={() => setView("recommendations")}
          >
            Recommendations
          </button>
          <button 
            className={`nav-button ${view === "profile" ? "active" : ""}`}
            onClick={() => setView("profile")}
          >
            Profile
          </button>
          <button className="nav-button logout" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      <main className="dashboard-content">
        {view === "recommendations" && <RecommendationsList user={user} />}
        {view === "profile" && <Profile user={user} />}
      </main>
    </div>
  );
}

export default Dashboard;
