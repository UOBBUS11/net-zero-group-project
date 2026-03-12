from flask import render_template, flash, redirect, url_for, request, session
from app import app, db

from app.models import User, Trip, TransportMode, Administrator
from app.forms import LoginForm, LogTripForm, EditRuleForm


def create_default_data():
    if not TransportMode.query.first():
        modes = [
            TransportMode(mode_name="Walking", emission_factor=0.0, base_points=50, points_per_km=10),
            TransportMode(mode_name="Bus", emission_factor=0.05, base_points=10, points_per_km=2),
            TransportMode(mode_name="Diesel Car", emission_factor=0.17, base_points=0, points_per_km=-5)
        ]
        db.session.add_all(modes)
        db.session.add(Administrator(username="admin", password="123"))
        db.session.commit()



@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    create_default_data()  
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        if form.is_admin.data:
            admin = Administrator.query.filter_by(username=username).first()
            if admin and admin.password == "123":  # 簡化驗證
                session['admin_id'] = admin.id
                return redirect(url_for('admin_panel'))
        else:
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, password="123")
                db.session.add(user)
                db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    leaderboard = User.query.order_by(User.current_score.desc()).all()
    return render_template('dashboard.html', user=user, leaderboard=leaderboard)


@app.route('/log_trip', methods=['GET', 'POST'])
def log_trip():
    if 'user_id' not in session: return redirect(url_for('login'))

    form = LogTripForm()
    form.mode.choices = [(m.id, f"{m.mode_name}") for m in TransportMode.query.all()]

    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        mode = TransportMode.query.get(form.mode.data)

        carbon = form.distance.data * mode.emission_factor
        score = mode.base_points + int(form.distance.data * mode.points_per_km)

        trip = Trip(distance_km=form.distance.data, carbon_emission=carbon,
                    score_earned=score, user=user, mode=mode)
        user.current_score += score

        db.session.add(trip)
        db.session.commit()

        recommendation = "Great Job!" if score > 0 else "High emission! Try walking next time."

        return render_template('result.html', trip=trip, recommendation=recommendation)

    return render_template('log_trip.html', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'admin_id' not in session: return redirect(url_for('login'))

    form = EditRuleForm()
    if form.validate_on_submit():

        flash('Rule Updated')

    modes = TransportMode.query.all()
    return render_template('admin.html', modes=modes, form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))