from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    current_score = db.Column(db.Float, default=0.0)
    profile_image = db.Column(db.String(255), nullable=True)

    trips = db.relationship('Trip', backref='user', lazy='dynamic')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class TransportMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode_name = db.Column(db.String(50), unique=True, nullable=False)
    emission_factor = db.Column(db.Float, nullable=False)
    base_points = db.Column(db.Float, nullable=False)
    points_per_km = db.Column(db.Float, nullable=False)


class SavedLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    normalized_name = db.Column(db.String(120), unique=True, nullable=False)
    in_emission_zone = db.Column(db.Boolean, default=False)
    zone_name = db.Column(db.String(50), nullable=True)


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance_km = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    carbon_emission = db.Column(db.Float, nullable=False)
    score_earned = db.Column(db.Float, nullable=False)

    location = db.Column(db.String(120), nullable=False)
    location_normalized = db.Column(db.String(120), nullable=False)
    entered_emission_zone = db.Column(db.Boolean, default=False)
    emission_zone_name = db.Column(db.String(50), nullable=True)

    score_breakdown = db.Column(db.String(500), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mode_id = db.Column(db.Integer, db.ForeignKey('transport_mode.id'), nullable=False)
    mode = db.relationship('TransportMode')


class Administrator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)