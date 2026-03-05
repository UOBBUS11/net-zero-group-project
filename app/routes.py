from flask import render_template, session, redirect, url_for, flash, request
from app import app, db
from app.models import User, TransportMode, Administrator
from app.forms import LoginForm



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

    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id'] # revised by member2

    user = User.query.get(user_id)

    leaderboard = User.query.order_by(User.current_score.desc()).all()

    return render_template('dashboard.html', user=user, leaderboard=leaderboard)



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


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/log_trip', methods=['GET', 'POST'])
def log_trip():
    return "<h2>Log Trip (Reserved for Member 3 & 4)</h2>"


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    return "<h2>Admin Panel (Reserved for Member 5)</h2>"