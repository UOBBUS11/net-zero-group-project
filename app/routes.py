<<<<<<< HEAD
from flask import render_template, redirect, url_for, session, flash
from app import app
from app.models import db, TransportMode, User, Administrator, Trip
from app.forms import LogTripForm, LoginForm
=======
from flask import render_template, session, redirect, url_for,flash
from app import app, db
from app.models import User, TransportMode, Administrator
from app.forms import EditRuleForm

>>>>>>> origin/AdminPanel-byAlim


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


<<<<<<< HEAD
=======

>>>>>>> origin/AdminPanel-byAlim
@app.before_request
def initialize():
    app.before_request_funcs[None].remove(initialize)
    create_default_data()


@app.route('/dashboard')
def dashboard():

<<<<<<< HEAD
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id'] # revised by member2
=======
    user_id = session.get('user_id', 1)
>>>>>>> origin/AdminPanel-byAlim

    user = User.query.get(user_id)

    leaderboard = User.query.order_by(User.current_score.desc()).all()

    return render_template('dashboard.html', user=user, leaderboard=leaderboard)


<<<<<<< HEAD

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if 'admin_id' in session:
        return redirect(url_for('admin_panel'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data


        if form.is_admin.data:
            admin = Administrator.query.filter_by(username=username).first()
            if admin and admin.password == "123":
                session['admin_id'] = admin.id
                flash('Admin Login Successful!', 'success')
                return redirect(url_for('admin_panel'))
            else:
                flash('Invalid Admin Credentials!', 'error')


        else:
            user = User.query.filter_by(username=username).first()
            if not user:

                user = User(username=username, password="123", current_score=0)
                db.session.add(user)
                db.session.commit()
                flash('New User Registered and Logged In!', 'success')
            else:
                flash('Login Successful!', 'success')


            session['user_id'] = user.id
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)
=======
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return "<h2>Login Page (Reserved for Member 2)</h2>"
>>>>>>> origin/AdminPanel-byAlim


@app.route('/logout')
def logout():
<<<<<<< HEAD
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
=======
    return "<h2>Logout (Reserved for Member 2)</h2>"
>>>>>>> origin/AdminPanel-byAlim


@app.route('/log_trip', methods=['GET', 'POST'])
def log_trip():
<<<<<<< HEAD
    form = LogTripForm()
    user_id = session.get('user_id')
    modes = TransportMode.query.all()

    # Optional robustness: if DB has no modes, seed once then re-query
    if not modes:
        create_default_data()
        modes = TransportMode.query.all()

    form.mode.choices = [(m.id, m.mode_name) for m in modes]

    if form.validate_on_submit():
        distance_input = form.distance.data
        mode_obj = TransportMode.query.get(form.mode.data)
        user_obj = User.query.get(user_id)
        new_trip = Trip(distance_km=distance_input, mode=mode_obj, user=user_obj)
        recommendation_text = new_trip.calculate_score()
        db.session.add(new_trip)
        db.session.commit()
        return render_template('result.html', trip=new_trip, recommendation=recommendation_text)
    return render_template('log_trip.html', form=form)
=======
    return "<h2>Log Trip (Reserved for Member 3 & 4)</h2>"
>>>>>>> origin/AdminPanel-byAlim


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
<<<<<<< HEAD
    return "<h2>Admin Panel (Reserved for Member 5)</h2>"
=======

    admin_id = session.get('admin_id', 1)


    form = EditRuleForm()


    modes = TransportMode.query.all()


    form.mode_id.choices = [(m.id, m.mode_name) for m in modes]


    if form.validate_on_submit():

        mode_to_update = TransportMode.query.get(form.mode_id.data)


        mode_to_update.base_points = form.base_points.data
        mode_to_update.points_per_km = form.points_per_km.data


        db.session.commit()


        flash(f'Rules for {mode_to_update.mode_name} updated successfully!', 'success')
        return redirect(url_for('admin_panel'))


    return render_template('admin.html', modes=modes, form=form)
>>>>>>> origin/AdminPanel-byAlim
