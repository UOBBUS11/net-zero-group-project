from flask import render_template, session, redirect, url_for
from app import app, db
from app.models import User, TransportMode, Administrator


def create_default_data():
    db.create_all()
    if not Administrator.query.first():
        db.session.add(Administrator(username="admin", password="123"))
    if not TransportMode.query.first():
        modes = [
            TransportMode(mode_name="Walking", emission_factor=0.0, base_points=50, points_per_km=10),
            TransportMode(mode_name="Bus", emission_factor=0.05, base_points=10, points_per_km=2),
            TransportMode(mode_name="Diesel Car", emission_factor=0.17, base_points=0, points_per_km=-5)
        ]
        db.session.add_all(modes)

    if not User.query.first():
        db.session.add(User(username="DemoUser", password="123", current_score=150))
    db.session.commit()



@app.before_request
def initialize():
    app.before_request_funcs[None].remove(initialize)
    create_default_data()


@app.route('/dashboard')
def dashboard():

    user_id = session.get('user_id', 1)

    user = User.query.get(user_id)

    leaderboard = User.query.order_by(User.current_score.desc()).all()

    return render_template('dashboard.html', user=user, leaderboard=leaderboard)



@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return "<h2>Login Page (Reserved for Member 2)</h2>"


@app.route('/logout')
def logout():
    return "<h2>Logout (Reserved for Member 2)</h2>"


@app.route('/log_trip', methods=['GET', 'POST'])
def log_trip():
    return "<h2>Log Trip (Reserved for Member 3 & 4)</h2>"


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    return "<h2>Admin Panel (Reserved for Member 5)</h2>"