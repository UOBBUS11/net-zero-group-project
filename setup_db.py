from datetime import datetime, timedelta

from app import app, db
from app.models import User, Trip, TransportMode, Administrator, SavedLocation
from app.routes import (
    calculate_trip_score,
    create_default_data,
    normalize_location,
    recalculate_user_score,
)


def get_mode(mode_name):
    mode = TransportMode.query.filter_by(mode_name=mode_name).first()
    if not mode:
        raise ValueError(f"Transport mode not found: {mode_name}")
    return mode


def create_user(username, password):
    user = User(username=username, current_score=0.0)
    user.set_password(password)
    db.session.add(user)
    return user


def create_saved_location(name, in_emission_zone=False, zone_name=None):
    normalized_name = normalize_location(name)

    location = SavedLocation.query.filter_by(normalized_name=normalized_name).first()
    if location:
        location.name = name
        location.in_emission_zone = in_emission_zone
        location.zone_name = zone_name
        return location

    location = SavedLocation(
        name=name,
        normalized_name=normalized_name,
        in_emission_zone=in_emission_zone,
        zone_name=zone_name,
    )
    db.session.add(location)
    return location


def create_trip(user, mode_name, distance_km, location_name, days_ago, enters_emission_zone=False):
    mode = get_mode(mode_name)
    normalized_location = normalize_location(location_name)

    saved_location = SavedLocation.query.filter_by(normalized_name=normalized_location).first()
    zone_name = None

    if saved_location:
        enters_emission_zone = saved_location.in_emission_zone
        zone_name = saved_location.zone_name

    carbon, score, score_breakdown, calculated_zone_name = calculate_trip_score(
        distance=distance_km,
        mode=mode,
        location=location_name,
        enters_emission_zone=enters_emission_zone,
    )

    if calculated_zone_name:
        zone_name = calculated_zone_name

    trip = Trip(
        distance_km=distance_km,
        timestamp=datetime.utcnow() - timedelta(days=days_ago),
        carbon_emission=carbon,
        score_earned=score,
        location=location_name,
        location_normalized=normalized_location,
        entered_emission_zone=enters_emission_zone,
        emission_zone_name=zone_name,
        score_breakdown=score_breakdown,
        user=user,
        mode=mode,
    )

    db.session.add(trip)
    return trip


def seed_saved_locations():
    locations = [
        ("Birmingham City Centre", True, "Birmingham Clean Air Zone"),
        ("London Euston", True, "London ULEZ"),
        ("University of Birmingham", False, None),
        ("Selly Oak", False, None),
        ("Birmingham New Street", True, "Birmingham Clean Air Zone"),
        ("Manchester Piccadilly", False, None),
        ("Coventry Station", False, None),
        ("Leeds City Centre", False, None),
        ("Bristol Temple Meads", False, None),
        ("Edinburgh Waverley", False, None),
    ]

    for name, in_emission_zone, zone_name in locations:
        create_saved_location(name, in_emission_zone, zone_name)


def seed_users_and_trips():
    users = {
        "matt": create_user("matt", "Carbon123!"),
        "amina": create_user("amina", "Carbon123!"),
        "josh": create_user("josh", "Carbon123!"),
        "sophie": create_user("sophie", "Carbon123!"),
        "liam": create_user("liam", "Carbon123!"),
    }

    db.session.flush()

    trip_data = {
        "matt": [
            ("Walking", 1.2, "Selly Oak", 0, False),
            ("Train", 8.4, "Birmingham New Street", 1, True),
            ("Bus", 5.7, "University of Birmingham", 2, False),
            ("Bicycle", 3.1, "Selly Oak", 3, False),
            ("Diesel Car", 12.5, "Birmingham City Centre", 4, True),
            ("Train", 112.0, "London Euston", 6, True),
            ("Electric Car", 18.0, "Coventry Station", 8, False),
            ("Walking", 0.9, "University of Birmingham", 10, False),
        ],
        "amina": [
            ("Bicycle", 4.0, "Selly Oak", 0, False),
            ("Train", 32.0, "Coventry Station", 1, False),
            ("Walking", 1.8, "University of Birmingham", 2, False),
            ("Bus", 7.2, "Birmingham City Centre", 3, True),
            ("Electric Bicycle", 6.5, "Selly Oak", 5, False),
            ("Train", 145.0, "Manchester Piccadilly", 7, False),
        ],
        "josh": [
            ("Petrol Car", 9.0, "Birmingham City Centre", 0, True),
            ("Diesel Car", 21.0, "Coventry Station", 1, False),
            ("Motorbike", 13.4, "Selly Oak", 2, False),
            ("Bus", 4.5, "University of Birmingham", 4, False),
            ("Petrol Car", 40.0, "Leeds City Centre", 6, False),
            ("Plane", 520.0, "Edinburgh Waverley", 12, False),
        ],
        "sophie": [
            ("Walking", 2.0, "University of Birmingham", 0, False),
            ("Walking", 1.5, "Selly Oak", 1, False),
            ("Bicycle", 5.0, "Birmingham City Centre", 2, True),
            ("Train", 118.0, "London Euston", 5, True),
            ("Electric Car", 24.0, "Coventry Station", 8, False),
            ("Bus", 6.1, "Birmingham New Street", 9, True),
        ],
        "liam": [
            ("Electric Car", 15.0, "Birmingham City Centre", 0, True),
            ("Train", 180.0, "Bristol Temple Meads", 2, False),
            ("Bus", 8.8, "Selly Oak", 3, False),
            ("Electric Motorbike", 11.0, "Coventry Station", 4, False),
            ("Petrol Car", 16.0, "Birmingham New Street", 6, True),
            ("Walking", 1.1, "University of Birmingham", 9, False),
        ],
    }

    for username, trips in trip_data.items():
        user = users[username]
        for mode_name, distance_km, location_name, days_ago, enters_emission_zone in trips:
            create_trip(
                user=user,
                mode_name=mode_name,
                distance_km=distance_km,
                location_name=location_name,
                days_ago=days_ago,
                enters_emission_zone=enters_emission_zone,
            )

    db.session.flush()

    for user in users.values():
        recalculate_user_score(user)


def reset_and_seed_database():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()

        print("Creating tables...")
        db.create_all()

        print("Creating default transport modes and admin account...")
        create_default_data()

        print("Creating saved locations...")
        seed_saved_locations()

        print("Creating users and trip history...")
        seed_users_and_trips()

        db.session.commit()

        print("Database setup complete.")
        print("Admin login: username='admin', password='example123'")
        print("Demo user logins: matt/amina/josh/sophie/liam, password='Carbon123!'")


if __name__ == "__main__":
    reset_and_seed_database()
