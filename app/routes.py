from flask import render_template, flash, redirect, url_for, request, session
from app import app, db
from app.models import User, Trip, TransportMode, Administrator, SavedLocation
from app.forms import (
    LoginForm,
    RegisterForm,
    LogTripForm,
    EditRuleForm,
    EditProfileForm,
    ChangePasswordForm
)


def normalize_username(username):
    return (username or "").strip()


def normalize_location(location):
    return " ".join((location or "").strip().lower().split())


def round_score(value):
    return round(max(0.0, min(10.0, value)), 1)


def infer_zone_name(location):
    normalized = normalize_location(location)
    if "birmingham" in normalized:
        return "Birmingham Clean Air Zone"
    if "london" in normalized:
        return "London ULEZ"
    return "Emission Zone"


def achievement_badge(score):
    if score >= 10.0:
        return "Carbon Legend"
    if score >= 9.0:
        return "Planet Guardian"
    if score >= 8.0:
        return "Eco Master"
    if score >= 7.0:
        return "Green Champion"
    if score >= 6.0:
        return "Low Carbon Commuter"
    if score >= 5.0:
        return "Conscious Traveller"
    if score >= 4.0:
        return "Carbon Catcher"
    if score >= 3.0:
        return "Improving Explorer"
    if score >= 2.0:
        return "Starter Saver"
    if score >= 1.0:
        return "First Step"
    return "Needs Improvement"


def badge_level(score):
    score_floor = int(max(0, min(10, score)))
    return score_floor


def leaderboard_title(rank):
    if rank == 1:
        return "👑 Champion of the Week"
    if rank == 2:
        return "🥈 Eco Elite"
    if rank == 3:
        return "🥉 Green Podium"
    if rank <= 10:
        return "🔥 Top 10 Contender"
    return "🌱 Rising Carbon Catcher"


def recalculate_user_score(user):
    trips = user.trips.all()
    if not trips:
        user.current_score = 0.0
        return

    average = sum(trip.score_earned for trip in trips) / len(trips)
    user.current_score = round_score(average)


def create_default_data():
    default_modes = [
        {"mode_name": "Walking", "emission_factor": 0.00, "base_points": 2.8, "points_per_km": 0.18},
        {"mode_name": "Bicycle", "emission_factor": 0.00, "base_points": 2.5, "points_per_km": 0.15},
        {"mode_name": "Electric Bicycle", "emission_factor": 0.01, "base_points": 2.1, "points_per_km": 0.12},
        {"mode_name": "Train", "emission_factor": 0.04, "base_points": 1.2, "points_per_km": 0.05},
        {"mode_name": "Bus", "emission_factor": 0.06, "base_points": 0.8, "points_per_km": 0.03},
        {"mode_name": "Electric Motorbike", "emission_factor": 0.03, "base_points": 0.8, "points_per_km": 0.02},
        {"mode_name": "Electric Car", "emission_factor": 0.07, "base_points": 0.3, "points_per_km": 0.01},
        {"mode_name": "Motorbike", "emission_factor": 0.11, "base_points": -0.8, "points_per_km": -0.03},
        {"mode_name": "Petrol Car", "emission_factor": 0.16, "base_points": -1.8, "points_per_km": -0.06},
        {"mode_name": "Diesel Car", "emission_factor": 0.19, "base_points": -2.4, "points_per_km": -0.08},
        {"mode_name": "Plane", "emission_factor": 0.25, "base_points": -3.3, "points_per_km": -0.10},
    ]

    for mode_data in default_modes:
        existing = TransportMode.query.filter_by(mode_name=mode_data["mode_name"]).first()
        if existing:
            existing.emission_factor = mode_data["emission_factor"]
            existing.base_points = mode_data["base_points"]
            existing.points_per_km = mode_data["points_per_km"]
        else:
            db.session.add(TransportMode(**mode_data))

    admin = Administrator.query.filter_by(username="admin").first()
    if not admin:
        admin = Administrator(username="admin")
        admin.set_password("example123")
        db.session.add(admin)
    else:
        if admin.password in ["123", "example123"]:
            admin.set_password("example123")

    db.session.commit()


def calculate_trip_score(distance, mode, location, enters_emission_zone):
    carbon = round(distance * mode.emission_factor, 3)

    score = 5.0
    breakdown = []

    score += mode.base_points
    breakdown.append(f"Mode weight {mode.base_points:+.1f}")

    distance_effect = distance * mode.points_per_km
    score += distance_effect
    breakdown.append(f"Distance effect {distance_effect:+.1f}")

    carbon_rate_penalty = mode.emission_factor * 10
    score -= carbon_rate_penalty
    breakdown.append(f"Carbon/km effect {-carbon_rate_penalty:+.1f}")

    practicality = 0.0
    mode_name = mode.mode_name.lower()

    if distance <= 2:
        if mode_name in ["walking", "bicycle", "electric bicycle"]:
            practicality += 1.0
        elif "car" in mode_name or mode_name == "motorbike":
            practicality -= 1.3
    elif distance <= 8:
        if mode_name in ["bicycle", "electric bicycle", "bus", "train"]:
            practicality += 0.8
        elif mode_name == "walking":
            practicality -= 0.4
    elif distance <= 40:
        if mode_name in ["train", "bus", "electric car"]:
            practicality += 0.7
        elif mode_name == "walking":
            practicality -= 2.0
        elif mode_name == "bicycle":
            practicality -= 0.8
    else:
        if mode_name in ["train", "electric car"]:
            practicality += 0.5
        elif mode_name in ["walking", "bicycle", "electric bicycle"]:
            practicality -= 2.5

    score += practicality
    breakdown.append(f"Practicality {practicality:+.1f}")

    zone_name = None
    if enters_emission_zone:
        zone_name = infer_zone_name(location)
        if "diesel" in mode_name or "petrol" in mode_name or mode_name == "motorbike":
            score -= 1.4
            breakdown.append("Emission zone penalty -1.4")
        elif "electric" in mode_name or mode_name in ["walking", "bicycle", "train", "bus"]:
            score += 0.6
            breakdown.append("Emission zone bonus +0.6")

    score = round_score(score)
    return carbon, score, " | ".join(breakdown), zone_name


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    create_default_data()
    form = LoginForm()

    if form.validate_on_submit():
        username = normalize_username(form.username.data)
        password = form.password.data

        if form.is_admin.data:
            admin = Administrator.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session.clear()
                session["admin_id"] = admin.id
                flash(f"Welcome back, admin {admin.username}.")
                return redirect(url_for("admin_panel"))

            flash("Invalid admin username or password.")
            return render_template("login.html", title="Login", form=form)

        if username.lower() == "admin":
            flash("The username 'admin' is reserved for administrator login.")
            return render_template("login.html", title="Login", form=form)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            flash(f"Welcome back, {user.username}.")
            return redirect(url_for("wall_of_fame"))

        flash("Invalid username or password.")
        return render_template("login.html", title="Login", form=form)

    return render_template("login.html", title="Login", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    create_default_data()
    form = RegisterForm()

    if form.validate_on_submit():
        username = normalize_username(form.username.data)
        password = form.password.data

        if username.lower() == "admin":
            flash("The username 'admin' is reserved and cannot be registered.")
            return render_template("register.html", title="Register", form=form)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username is already taken.")
            return render_template("register.html", title="Register", form=form)

        new_user = User(username=username, current_score=0.0)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/dashboard")
def dashboard():
    return redirect(url_for("wall_of_fame"))


@app.route("/wall-of-fame")
def wall_of_fame():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.pop("user_id", None)
        flash("Session expired. Please log in again.")
        return redirect(url_for("login"))

    users = User.query.order_by(User.current_score.desc(), User.username.asc()).all()

    leaderboard = []
    for index, entry in enumerate(users, start=1):
        leaderboard.append({
            "rank": index,
            "user": entry,
            "badge": achievement_badge(entry.current_score),
            "badge_level": badge_level(entry.current_score),
            "title": leaderboard_title(index),
            "is_you": entry.id == user.id
        })

    total_users = len(users)
    your_rank = next((item["rank"] for item in leaderboard if item["is_you"]), None)

    return render_template(
        "dashboard.html",
        user=user,
        leaderboard=leaderboard,
        your_rank=your_rank,
        total_users=total_users,
        your_badge=achievement_badge(user.current_score),
        your_badge_level=badge_level(user.current_score)
    )


@app.route("/trip-history")
def trip_history():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.pop("user_id", None)
        flash("Session expired. Please log in again.")
        return redirect(url_for("login"))

    history_query = Trip.query.filter_by(user_id=user.id).join(TransportMode)

    search_date = (request.args.get("date") or "").strip()
    search_location = (request.args.get("location") or "").strip()
    search_mode = (request.args.get("mode") or "").strip()

    if search_date:
        history_query = history_query.filter(db.func.date(Trip.timestamp) == search_date)

    if search_location:
        history_query = history_query.filter(Trip.location.ilike(f"%{search_location}%"))

    if search_mode:
        history_query = history_query.filter(TransportMode.mode_name == search_mode)

    history = history_query.order_by(Trip.timestamp.desc()).all()
    all_modes = TransportMode.query.order_by(TransportMode.mode_name.asc()).all()

    return render_template(
        "trip_history.html",
        user=user,
        history=history,
        all_modes=all_modes,
        search_date=search_date,
        search_location=search_location,
        search_mode=search_mode
    )


@app.route("/log_trip", methods=["GET", "POST"])
def log_trip():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.pop("user_id", None)
        flash("Session expired. Please log in again.")
        return redirect(url_for("login"))

    form = LogTripForm()
    form.mode.choices = [(m.id, m.mode_name) for m in TransportMode.query.order_by(TransportMode.mode_name.asc()).all()]

    known_locations = SavedLocation.query.order_by(SavedLocation.name.asc()).all()
    known_location_map = {
        item.normalized_name: {
            "name": item.name,
            "in_emission_zone": item.in_emission_zone,
            "zone_name": item.zone_name or ""
        }
        for item in known_locations
    }

    if form.validate_on_submit():
        mode = TransportMode.query.get(form.mode.data)

        if not mode:
            flash("Selected transport mode is invalid.")
            return redirect(url_for("log_trip"))

        location = (form.location.data or "").strip()
        normalized_location = normalize_location(location)

        saved_location = SavedLocation.query.filter_by(normalized_name=normalized_location).first()

        enters_emission_zone = form.enters_emission_zone.data
        zone_name = None

        if saved_location:
            enters_emission_zone = saved_location.in_emission_zone
            zone_name = saved_location.zone_name
        else:
            if enters_emission_zone:
                zone_name = infer_zone_name(location)

            new_location = SavedLocation(
                name=location,
                normalized_name=normalized_location,
                in_emission_zone=enters_emission_zone,
                zone_name=zone_name
            )
            db.session.add(new_location)

        carbon, score, score_breakdown, calculated_zone_name = calculate_trip_score(
            distance=form.distance.data,
            mode=mode,
            location=location,
            enters_emission_zone=enters_emission_zone
        )

        if calculated_zone_name:
            zone_name = calculated_zone_name

        trip = Trip(
            distance_km=form.distance.data,
            carbon_emission=carbon,
            score_earned=score,
            location=location,
            location_normalized=normalized_location,
            entered_emission_zone=enters_emission_zone,
            emission_zone_name=zone_name,
            score_breakdown=score_breakdown,
            user=user,
            mode=mode
        )

        db.session.add(trip)
        db.session.flush()

        recalculate_user_score(user)
        db.session.commit()

        if score >= 8.5:
            recommendation = "Excellent choice. This was a very strong low-carbon trip."
        elif score >= 6.5:
            recommendation = "Good trip overall. A solid sustainable choice."
        elif score >= 4.5:
            recommendation = "Reasonable trip, but there may be greener alternatives."
        else:
            recommendation = "This trip scored poorly. Try a cleaner or more practical transport choice next time."

        return render_template("result.html", trip=trip, recommendation=recommendation, user=user)

    return render_template(
        "log_trip.html",
        form=form,
        known_location_map=known_location_map
    )


@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if "admin_id" not in session:
        flash("Admin access only.")
        return redirect(url_for("login"))

    admin = Administrator.query.get(session["admin_id"])
    if not admin:
        session.pop("admin_id", None)
        flash("Admin session expired. Please log in again.")
        return redirect(url_for("login"))

    form = EditRuleForm()
    modes = TransportMode.query.order_by(TransportMode.mode_name.asc()).all()
    form.mode_id.choices = [(m.id, m.mode_name) for m in modes]

    if form.validate_on_submit():
        mode = TransportMode.query.get(form.mode_id.data)
        if mode:
            mode.emission_factor = form.emission_factor.data
            mode.base_points = form.base_points.data
            mode.points_per_km = form.points_per_km.data
            db.session.commit()
            flash(f"Updated scoring rule for {mode.mode_name}.")
            return redirect(url_for("admin_panel"))

    users = User.query.order_by(User.current_score.desc(), User.username.asc()).all()
    locations = SavedLocation.query.order_by(SavedLocation.name.asc()).all()
    recent_trips = Trip.query.order_by(Trip.timestamp.desc()).limit(20).all()

    return render_template(
        "admin.html",
        admin=admin,
        modes=modes,
        users=users,
        locations=locations,
        recent_trips=recent_trips,
        form=form
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.pop("user_id", None)
        flash("Session expired. Please log in again.")
        return redirect(url_for("login"))

    trip_count = Trip.query.filter_by(user_id=user.id).count()
    latest_trip = Trip.query.filter_by(user_id=user.id).order_by(Trip.timestamp.desc()).first()

    edit_profile_form = EditProfileForm(prefix="profile")
    change_password_form = ChangePasswordForm(prefix="password")

    if request.method == "GET":
        edit_profile_form.username.data = user.username

    if request.method == "POST":
        if edit_profile_form.submit.data:
            if edit_profile_form.validate():
                new_username = normalize_username(edit_profile_form.username.data)

                if new_username.lower() == "admin":
                    flash("The username 'admin' is reserved and cannot be used.")
                else:
                    existing_user = User.query.filter_by(username=new_username).first()
                    if existing_user and existing_user.id != user.id:
                        flash("That username is already taken.")
                    else:
                        user.username = new_username
                        db.session.commit()
                        flash("Username updated successfully.")
                        return redirect(url_for("profile"))
            else:
                flash("Please correct the username form errors.")

        elif change_password_form.submit.data:
            if change_password_form.validate():
                current_password = change_password_form.current_password.data
                new_password = change_password_form.new_password.data

                if not user.check_password(current_password):
                    flash("Your current password is incorrect.")
                elif current_password == new_password:
                    flash("Your new password must be different from the current password.")
                else:
                    user.set_password(new_password)
                    db.session.commit()
                    flash("Password updated successfully.")
                    return redirect(url_for("profile"))
            else:
                flash("Please correct the password form errors.")

    # Developer note:
    # If a future dashboard-summary feature is added, this profile route is the right place
    # to assemble and render it so users see that summary after clicking the Profile tab.
    # Example additions later:
    # - total trips
    # - average carbon per trip
    # - recent achievements
    # - weekly/monthly sustainability summary
    # - streaks and milestone cards

    return render_template(
        "profile.html",
        user=user,
        trip_count=trip_count,
        latest_trip=latest_trip,
        edit_profile_form=edit_profile_form,
        change_password_form=change_password_form,
        achievement_badge=achievement_badge
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))