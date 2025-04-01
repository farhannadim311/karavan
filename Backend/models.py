# models.py

from datetime import datetime
from database import db

# Example "User" model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Basic user preferences
    prefers_solitude = db.Column(db.Boolean, default=False)
    prefers_fishing = db.Column(db.Boolean, default=False)
    prefers_hiking = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "prefers_solitude": self.prefers_solitude,
            "prefers_fishing": self.prefers_fishing,
            "prefers_hiking": self.prefers_hiking
        }

# Example "CampReview" model for user-generated content
class CampReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campsite_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, default=0)  # 1-5 star rating
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "campsite_name": self.campsite_name,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat()
        }
