from flask import render_template, flash, redirect, url_for, request, session
from app import app, db
from app.models import User, Trip, TransportMode, Administrator
from app.forms import LoginForm, RegisterForm, LogTripForm, EditRuleForm


def create_default_data():
    if not TransportMode.query.first():
        modes = [
            TransportMode(mode_name="Walking", emission_factor=0.0, base_points=50, points_per_km=10),
            TransportMode(mode_name="Bus", emission_factor=0.05, base_points=10, points_per_km=2),
            TransportMode(mode_name="Diesel Car", emission_factor=0.17, base_points=0, points_per_km=-5)
        ]
        db.session.add_all(modes)

    admin = Administrator.query.filter_by(username="admin").first()

    if not admin:
        admin = Administrator(username="admin")
        admin.set_password("example123")
        db.session.add(admin)
    else:
        # Helps if old dev DB still has plain-text admin password
        if admin.password in ["123", "example123"]:
            admin.set_password("example123")

    db.session.commit()


def normalize_username(username):
    return (username or "").strip()


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    create_default_data()
    form = LoginForm()

    if request.method == 'GET':
        if session.get('admin_id'):
            return redirect(url_for('admin_panel'))
        if session.get('user_id'):
            return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        username = normalize_username(form.username.data)
        password = form.password.data

        if form.is_admin.data:
            admin = Administrator.query.filter_by(username=username).first()

            if admin and admin.check_password(password):
                session.clear()
                session['admin_id'] = admin.id
                flash('Admin login successful.')
                return redirect(url_for('admin_panel'))

            flash('Invalid admin username or password.')
            return render_template('login.html', title='Login', form=form)

        if username.lower() == 'admin':
            flash("The username 'admin' is reserved for administrator login.")
            return render_template('login.html', title='Login', form=form)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}.')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.')
        return render_template('login.html', title='Login', form=form)

    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    create_default_data()
    form = RegisterForm()

    if form.validate_on_submit():
        username = normalize_username(form.username.data)
        password = form.password.data

        if username.lower() == 'admin':
            flash("The username 'admin' is reserved and cannot be registered.")
            return render_template('register.html', title='Register', form=form)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('That username is already taken.')
            return render_template('register.html', title='Register', form=form)

        new_user = User(username=username, current_score=0)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('Session expired. Please log in again.')
        return redirect(url_for('login'))

    leaderboard = User.query.order_by(User.current_score.desc(), User.username.asc()).all()
    return render_template('dashboard.html', user=user, leaderboard=leaderboard)


@app.route('/log_trip', methods=['GET', 'POST'])
def log_trip():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('Session expired. Please log in again.')
        return redirect(url_for('login'))

    form = LogTripForm()
    form.mode.choices = [(m.id, m.mode_name) for m in TransportMode.query.all()]

    if form.validate_on_submit():
        mode = TransportMode.query.get(form.mode.data)

        if not mode:
            flash('Selected transport mode is invalid.')
            return redirect(url_for('log_trip'))

        carbon = form.distance.data * mode.emission_factor
        score = mode.base_points + int(form.distance.data * mode.points_per_km)

        trip = Trip(
            distance_km=form.distance.data,
            carbon_emission=carbon,
            score_earned=score,
            user=user,
            mode=mode
        )

        user.current_score += score

        db.session.add(trip)
        db.session.commit()

        recommendation = "Great job!" if score > 0 else "High emission! Try a greener option next time."

        return render_template('result.html', trip=trip, recommendation=recommendation)

    return render_template('log_trip.html', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'admin_id' not in session:
        flash('Admin access only.')
        return redirect(url_for('login'))

    admin = Administrator.query.get(session['admin_id'])
    if not admin:
        session.pop('admin_id', None)
        flash('Admin session expired. Please log in again.')
        return redirect(url_for('login'))

    form = EditRuleForm()

    if form.validate_on_submit():
        flash('Rule Updated')

    modes = TransportMode.query.all()
    return render_template('admin.html', modes=modes, form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))