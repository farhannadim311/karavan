# config.py

# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///camping.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API URLs
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    GEMINI_API_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    )
    # If you have a Light Pollution or Campsite API, put them here:
    # LIGHT_POLLUTION_API_URL = "..."
    # CAMPSITE_API_URL = "..."

    # If you have an explicit Light Pollution or Campsite API key, add them:
    # LIGHT_POLLUTION_API_KEY = os.getenv("LIGHT_POLLUTION_API_KEY")
    # CAMPSITE_API_KEY = os.getenv("CAMPSITE_API_KEY")

    # Application Settings
    MAX_RECOMMENDATION_DISTANCE = 50  # km
    MAX_RECOMMENDATIONS = 10
    CACHE_TIMEOUT = 3600  # 1 hour in seconds
