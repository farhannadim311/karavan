# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from recommendation import recommend_campsites
from services.maps_service import get_location_details, get_nearby_places, get_hiking_trails
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import time

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    return app

app = create_app()

# Example User model right here (overriding or duplicating from models.py is optional)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    prefers_fishing = db.Column(db.Boolean, default=False)
    prefers_hiking = db.Column(db.Boolean, default=False)
    prefers_solitude = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'prefers_fishing': self.prefers_fishing,
            'prefers_hiking': self.prefers_hiking,
            'prefers_solitude': self.prefers_solitude,
            'created_at': self.created_at.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

def generate_token(user_id):
    """Generate JWT token for user"""
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

@app.route("/")
def index():
    return jsonify({"message": "Welcome to the AI-Powered Camping/Stargazing App!"})

# User sign-up
@app.route("/api/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        hashed_pw = generate_password_hash(password)
        user = User(email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()

        # Generate token
        token = generate_token(user.id)

        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict(),
            "token": token
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# User login
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate token
        token = generate_token(user.id)

        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "token": token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update user preferences
@app.route("/api/preferences", methods=["POST"])
def update_preferences():
    try:
        data = request.json
        user_id = data.get("user_id")
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.prefers_fishing = data.get("prefers_fishing", user.prefers_fishing)
        user.prefers_hiking = data.get("prefers_hiking", user.prefers_hiking)
        user.prefers_solitude = data.get("prefers_solitude", user.prefers_solitude)

        db.session.commit()
        return jsonify({"message": "Preferences updated", "user": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Get location details from address
@app.route("/api/location", methods=["GET"])
def get_location():
    address = request.args.get("address")
    if not address:
        return jsonify({"error": "Address is required"}), 400

    location = get_location_details(address)
    if not location:
        return jsonify({"error": "Location not found"}), 404

    return jsonify(location)

# Get nearby places
@app.route("/api/places", methods=["GET"])
def get_places():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radius = request.args.get("radius", type=int, default=50000)
    place_type = request.args.get("type", default="campground")

    if lat is None or lon is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    places = get_nearby_places(lat, lon, radius, place_type)
    return jsonify(places)

# Get hiking trails
@app.route("/api/trails", methods=["GET"])
def get_trails():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radius = request.args.get("radius", type=int, default=50000)

    if lat is None or lon is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    trails = get_hiking_trails(lat, lon, radius)
    return jsonify(trails)

# Get recommendations
@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():
    try:
        data = request.json
        print(f"Received request data: {data}")  # Add logging
        
        user_lat = data.get("lat")
        user_lon = data.get("lng")  # Changed from lon to lng
        user_id = data.get("user_id")
        
        if not user_lat or not user_lon:
            return jsonify({"error": "Latitude and longitude are required"}), 400
            
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Get user preferences
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_preferences = {
            "prefers_fishing": user.prefers_fishing,
            "prefers_hiking": user.prefers_hiking,
            "prefers_solitude": user.prefers_solitude
        }

        print(f"Getting recommendations for user {user_id} at coordinates: {user_lat}, {user_lon}")
        print(f"User preferences: {user_preferences}")

        # Get recommendations
        recommendations = recommend_campsites(user_lat, user_lon, user_preferences)
        
        if not recommendations:
            return jsonify({
                "recommendations": [],
                "ai_summary": {
                    "text": "No recommendations found for this location.",
                    "timestamp": int(time.time())
                }
            })

        return jsonify(recommendations)

    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        return jsonify({
            "error": str(e),
            "recommendations": [],
            "ai_summary": {
                "text": "An error occurred while generating recommendations.",
                "timestamp": int(time.time())
            }
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
