from app import app, db
from app.models import User, Trip, TransportMode, SavedLocation
from datetime import datetime, timedelta
import random
from app.routes import calculate_trip_score, recalculate_user_score, create_default_data

def seed():
    with app.app_context():
        # Ensure default transport modes and admin are initialized
        create_default_data()

        print("Populating test users...")
        usernames = ["alim_uzzaman", "bob_walker", "charlie_driver", "diana_cyclist"]
        users = []
        for uname in usernames:
            user = User.query.filter_by(username=uname).first()
            if not user:
                user = User(username=uname, current_score=0.0)
                user.set_password("password123")
                db.session.add(user)
                users.append(user)
            else:
                users.append(user)
        db.session.commit()

        # Fetch all modes
        modes = TransportMode.query.all()
        if not modes:
            print("No transport modes found.")
            return

        print("Populating test locations...")
        locations = [
            ("Birmingham City Centre", True),
            ("London Soho", True),
            ("Coventry Outer", False),
            ("Wolverhampton Suburb", False)
        ]
        
        for loc_name, in_zone in locations:
            norm_name = " ".join(loc_name.lower().split())
            loc = SavedLocation.query.filter_by(normalized_name=norm_name).first()
            if not loc:
                loc = SavedLocation(
                    name=loc_name, 
                    normalized_name=norm_name, 
                    in_emission_zone=in_zone,
                    zone_name="Birmingham Clean Air Zone" if "Birmingham" in loc_name else ("London ULEZ" if "London" in loc_name else None)
                )
                db.session.add(loc)
        db.session.commit()

        print("Generating mock trips...")
        for user in users:
            # Check if user already has trips to avoid duplicating too much on multiple runs
            if user.trips.count() > 0:
                print(f"User {user.username} already has trips, skipping...")
                continue
                
            # Give each user 5 to 10 random trips over the last 14 days
            num_trips = random.randint(5, 10)
            for _ in range(num_trips):
                mode = random.choice(modes)
                loc_name, in_zone = random.choice(locations)
                norm_name = " ".join(loc_name.lower().split())
                distance = round(random.uniform(1.0, 25.0), 1)
                
                # Calculate scores properly using your existing logic
                carbon, score, score_breakdown, zone_name = calculate_trip_score(
                    distance=distance,
                    mode=mode,
                    location=loc_name,
                    enters_emission_zone=in_zone
                )
                
                # Random past date
                days_ago = random.randint(0, 14)
                trip_date = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0,23))

                trip = Trip(
                    distance_km=distance,
                    timestamp=trip_date,
                    carbon_emission=carbon,
                    score_earned=score,
                    location=loc_name,
                    location_normalized=norm_name,
                    entered_emission_zone=in_zone,
                    emission_zone_name=zone_name,
                    score_breakdown=score_breakdown,
                    user=user,
                    mode=mode
                )
                db.session.add(trip)
            
            db.session.flush()
            recalculate_user_score(user)

        db.session.commit()
        print("✅ Test data successfully populated!")
        print("Login with any of these users using password: password123")

if __name__ == "__main__":
    seed()
