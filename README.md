# Karav-n: AI-Powered Camping & Stargazing App (WIP)

An end-to-end application that helps you discover ideal camping and stargazing spots. The project integrates **Flask** (Python) and **React**, pulling data from **Google Maps**, **OpenWeatherMap**, and an AI-based recommendation engine (via Gemini) to rank campsites based on user preferences, weather, and estimated light pollution.


---

## Overview
**Karav-n** is designed to simplify the process of finding great campsites. It:
1. Geolocates user input (e.g., address) via Google Maps (or Geopy).
2. Retrieves camping spots, hiking trails, and weather data.
3. Scores each site based on user preferences (like fishing or solitude), travel distance, and atmospheric conditions.
4. Generates a personalized recommendation using an AI service (Gemini).

---

## Features
1. **Location Search & Directions**  
   - Convert an address to latitude/longitude using Geopy.  
   - Google Maps Places API to locate nearby campsites, hiking trails, etc.

2. **Weather Integration**  
   - Real-time weather (OpenWeatherMap) for each site—clouds, temp, rain, wind speed.  
   - Light pollution “score” estimated from weather or optional Bortle scale API.

3. **AI-Driven Recommendations**  
   - A custom scoring algorithm plus an AI summary.  
   - Factors user preferences (hiking, fishing, solitude), weather, and distance.

4. **Simple CRUD Patterns** (optional)  
   - Example database models for user reviews, preferences, etc. using SQLAlchemy.

---

## Tech Stack
- **Backend**:  
  - [Python](https://www.python.org/)  
  - [Flask](https://flask.palletsprojects.com/) (RESTful routes)  
  - [SQLAlchemy](https://www.sqlalchemy.org/) (database access)
- **Frontend**:  
  - [React](https://reactjs.org/)  
  - [Axios](https://github.com/axios/axios) (HTTP client)
- **APIs**:  
  - [Google Maps] 
  - [OpenWeatherMp] 
    [Gemini AI service]

---

## Instructions on how to run

## Backend (Flask)

# 1) Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

# 2) Install Python dependencies
pip install -r requirements.txt

# 3) # (Replace placeholder API keys with real ones)


# 4) Start the Flask server
python run.py
------------
## Frontend (React)
# 1) Install Node dependencies
npm install

# If your React app is in a 'frontend' folder:
# cd frontend
# npm install

# 2) Start the React dev server
npm run start

# By default, it'll be served at http://localhost:3000/

