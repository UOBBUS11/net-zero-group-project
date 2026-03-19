import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest

from app import app, db
from app.models import User, Administrator, TransportMode
from app.routes import create_default_data


@pytest.fixture
def test_app():
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="test-secret",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        create_default_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def app_context(test_app):
    with test_app.app_context():
        yield


@pytest.fixture
def normal_user(app_context):
    user = User(username="matt", current_score=0.0)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(app_context):
    user = User(username="alice", current_score=8.7)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def third_user(app_context):
    user = User(username="bob", current_score=4.2)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app_context):
    admin = Administrator.query.filter_by(username="admin").first()
    if admin is None:
        admin = Administrator(username="admin")
        admin.set_password("example123")
        db.session.add(admin)
        db.session.commit()
    return admin


@pytest.fixture
def walking_mode(app_context):
    return TransportMode.query.filter_by(mode_name="Walking").first()


@pytest.fixture
def petrol_mode(app_context):
    return TransportMode.query.filter_by(mode_name="Petrol Car").first()


@pytest.fixture
def train_mode(app_context):
    return TransportMode.query.filter_by(mode_name="Train").first()


def login_user(client, username="matt", password="password123"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "submit": "Login",
        },
        follow_redirects=True,
    )


def login_admin(client, username="admin", password="example123"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "is_admin": "y",
            "submit": "Login",
        },
        follow_redirects=True,
    )