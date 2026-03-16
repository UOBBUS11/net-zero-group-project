from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    current_score = db.Column(db.Integer, default=0)

    trips = db.relationship('Trip', backref='user', lazy='dynamic')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class TransportMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode_name = db.Column(db.String(50))
    emission_factor = db.Column(db.Float)
    base_points = db.Column(db.Integer)
    points_per_km = db.Column(db.Integer)


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance_km = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    carbon_emission = db.Column(db.Float)
    score_earned = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mode_id = db.Column(db.Integer, db.ForeignKey('transport_mode.id'))
    mode = db.relationship('TransportMode')


class Administrator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)