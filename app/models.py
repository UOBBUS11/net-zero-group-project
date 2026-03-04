from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    current_score = db.Column(db.Integer, default=0)
    trips = db.relationship('Trip', backref='user', lazy=True)

class TransportMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode_name = db.Column(db.String(50), nullable=False)
    emission_factor = db.Column(db.Float, nullable=False)
    base_points = db.Column(db.Integer, nullable=False)
    points_per_km = db.Column(db.Integer, nullable=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance_km = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    carbon_emission = db.Column(db.Float, nullable=False)
    score_earned = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mode_id = db.Column(db.Integer, db.ForeignKey('transport_mode.id'), nullable=False)
    mode = db.relationship('TransportMode')

class Administrator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)