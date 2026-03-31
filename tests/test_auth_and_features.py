import io
from datetime import datetime

from app import db
from app.models import Trip, User
from tests.conftest import login_user, login_admin

# T-MB-00: Valid user registration creates a new account successfully
def test_register_valid_user(client, app_context):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "password123",
            "confirm_password": "password123",
            "submit": "Create Account",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Account created successfully. Please log in." in response.data
    assert User.query.filter_by(username="newuser").first() is not None


# T-MB-00A: Reserved username 'admin' cannot be registered by a normal user
def test_register_rejects_reserved_admin_username(client, app_context):
    response = client.post(
        "/register",
        data={
            "username": "admin",
            "password": "password123",
            "confirm_password": "password123",
            "submit": "Create Account",
        },
        follow_redirects=True,
    )

    assert b"reserved and cannot be registered" in response.data
    assert b"admin" in response.data


# T-MB-00B: Duplicate usernames are rejected at registration
def test_register_rejects_duplicate_username(client, app_context, normal_user):
    response = client.post(
        "/register",
        data={
            "username": "matt",
            "password": "password123",
            "confirm_password": "password123",
            "submit": "Create Account",
        },
        follow_redirects=True,
    )

    assert b"That username is already taken." in response.data


# T-MB-00C: Valid normal user login succeeds
def test_login_valid_normal_user(client, normal_user):
    response = login_user(client)

    assert response.status_code == 200
    assert b"Welcome back, matt." in response.data
    assert b"Dashboard" in response.data


# T-MB-00D: Username 'admin' is blocked in the normal user login flow
def test_login_blocks_admin_username_in_normal_login(client, admin_user):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "example123",
            "submit": "Login",
        },
        follow_redirects=True,
    )

    assert b"reserved for administrator login" in response.data
    assert b"admin" in response.data


# T-MB-00E: Admin login succeeds through the administrator login path
def test_admin_login_works(client, admin_user):
    response = login_admin(client)

    assert response.status_code == 200
    assert b"Welcome back, admin admin." in response.data
    assert b"Admin Panel" in response.data


# T-MB-05: Wall of Fame orders users by highest score first
def test_wall_of_fame_orders_users_by_score(client, normal_user, second_user, third_user):
    login_user(client)

    response = client.get("/wall-of-fame")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "alice" in html and "matt" in html and "bob" in html
    assert html.index("alice") < html.index("bob")


# T-MB-01: Valid trip log creates a trip and updates the user's score
def test_log_trip_creates_trip_and_updates_score(client, app_context, normal_user, walking_mode):
    login_user(client)

    response = client.post(
        "/log_trip",
        data={
            "distance": "1.5",
            "location": "Birmingham City Centre",
            "mode": str(walking_mode.id),
            "enters_emission_zone": "y",
            "submit": "Log Trip",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Trip Logged Successfully" in response.data

    trip = Trip.query.filter_by(location="Birmingham City Centre").first()
    assert trip is not None
    assert trip.entered_emission_zone is True
    assert trip.emission_zone_name == "Birmingham Clean Air Zone"
    assert trip.score_earned >= 0
    assert normal_user.current_score == trip.score_earned


# T-MB-02: Invalid trip distance is rejected during trip logging
def test_log_trip_rejects_invalid_distance(client, normal_user, walking_mode):
    login_user(client)

    response = client.post(
        "/log_trip",
        data={
            "distance": "-1",
            "location": "Birmingham",
            "mode": str(walking_mode.id),
            "submit": "Log Trip",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Log a New Trip" in response.data
    assert b"Distance must be positive" in response.data


# T-MB-08: Trip history can be filtered by location
def test_trip_history_filters_by_location(client, app_context, normal_user, walking_mode, train_mode):
    trip1 = Trip(
        distance_km=2.0,
        carbon_emission=0.0,
        score_earned=8.0,
        location="Birmingham",
        location_normalized="birmingham",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="",
        user=normal_user,
        mode=walking_mode,
    )
    trip2 = Trip(
        distance_km=10.0,
        carbon_emission=0.4,
        score_earned=6.0,
        location="London",
        location_normalized="london",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="",
        user=normal_user,
        mode=train_mode,
    )
    db.session.add_all([trip1, trip2])
    db.session.commit()

    login_user(client)
    response = client.get("/trip-history?location=Birmingham")

    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Birmingham" in html
    assert "London" not in html


# T-MB-09: Trip history can be filtered by transport mode
def test_trip_history_filters_by_mode(client, app_context, normal_user, walking_mode, train_mode):
    trip1 = Trip(
        distance_km=2.0,
        carbon_emission=0.0,
        score_earned=8.0,
        location="Birmingham",
        location_normalized="birmingham",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="walk breakdown",
        user=normal_user,
        mode=walking_mode,
    )
    trip2 = Trip(
        distance_km=10.0,
        carbon_emission=0.4,
        score_earned=6.0,
        location="London",
        location_normalized="london",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="train breakdown",
        user=normal_user,
        mode=train_mode,
    )
    db.session.add_all([trip1, trip2])
    db.session.commit()

    login_user(client)
    response = client.get("/trip-history?mode=Walking")

    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "1 result(s)" in html
    assert "Birmingham" in html
    assert "walk breakdown" in html
    assert "train breakdown" not in html


# T-MB-10A: Profile username can be updated successfully
def test_profile_username_update(client, app_context, normal_user):
    login_user(client)

    response = client.post(
        "/profile",
        data={
            "profile-username": "mattnew",
            "profile-submit": "Update Username",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Username updated successfully." in response.data
    assert User.query.filter_by(username="mattnew").first() is not None


# T-MB-10B: Password change is rejected when the current password is wrong
def test_profile_password_change_rejects_wrong_current_password(client, app_context, normal_user):
    login_user(client)

    response = client.post(
        "/profile",
        data={
            "password-current_password": "wrongpass",
            "password-new_password": "newpassword123",
            "password-confirm_new_password": "newpassword123",
            "password-submit": "Change Password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Your current password is incorrect." in response.data


# T-MB-10C: Password change succeeds with the correct current password
def test_profile_password_change_succeeds(client, app_context, normal_user):
    login_user(client)

    response = client.post(
        "/profile",
        data={
            "password-current_password": "password123",
            "password-new_password": "newpassword123",
            "password-confirm_new_password": "newpassword123",
            "password-submit": "Change Password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Password updated successfully." in response.data

    updated_user = User.query.filter_by(username="matt").first()
    assert updated_user.check_password("newpassword123") is True


# T-JE-01: Login sends normal user to dashboard by default
def test_login_lands_on_dashboard_for_my_feature(client, normal_user):
    response = login_user(client)

    assert response.status_code == 200
    assert b"Welcome back, matt." in response.data
    assert b"Dashboard" in response.data


# T-JE-02: Profile dropdown shows dashboard, account settings, and logout
def test_profile_dropdown_items_visible_for_my_feature(client, normal_user):
    login_user(client)
    response = client.get("/profile")

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Account Settings" in response.data
    assert b"Logout" in response.data


# T-JE-03: Logout from the profile dropdown returns the user to login
def test_logout_works_for_my_feature(client, normal_user):
    login_user(client)
    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out." in response.data or b"Login" in response.data


# T-JE-04: Profile page shows the profile picture upload form
def test_profile_page_shows_upload_form_for_my_feature(client, normal_user):
    login_user(client)
    response = client.get("/profile")

    assert response.status_code == 200
    assert b"Profile Picture" in response.data
    assert b"Upload Photo" in response.data


# T-JE-05: Valid profile image upload succeeds
def test_profile_image_upload_valid_file_for_my_feature(client, app_context, normal_user):
    login_user(client)

    response = client.post(
        "/profile",
        data={
            "avatar-profile_image": (io.BytesIO(b"fake image data"), "avatar.png"),
            "avatar-submit": "Upload Photo",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Profile picture updated successfully." in response.data


# T-JE-06: Invalid profile image upload is rejected
def test_profile_image_upload_rejects_invalid_file_type_for_my_feature(client, app_context, normal_user):
    login_user(client)

    response = client.post(
        "/profile",
        data={
            "avatar-profile_image": (io.BytesIO(b"not an image"), "notes.txt"),
            "avatar-submit": "Upload Photo",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Images only please." in response.data or b"Please upload a valid image file." in response.data


# T-JE-07: Trip history requires login
def test_trip_history_requires_login_for_my_feature(client):
    response = client.get("/trip-history", follow_redirects=True)

    assert response.status_code == 200
    assert b"Please log in first." in response.data or b"Login" in response.data


# T-JE-08: Trip history can be filtered by date
def test_trip_history_filters_by_date_for_my_feature(client, app_context, normal_user, walking_mode, train_mode):
    trip1 = Trip(
        distance_km=2.0,
        timestamp=datetime(2026, 3, 30, 9, 0, 0),
        carbon_emission=0.0,
        score_earned=8.0,
        location="Birmingham",
        location_normalized="birmingham",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="walk breakdown",
        user=normal_user,
        mode=walking_mode,
    )
    trip2 = Trip(
        distance_km=10.0,
        timestamp=datetime(2026, 3, 31, 10, 30, 0),
        carbon_emission=0.4,
        score_earned=6.0,
        location="London",
        location_normalized="london",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="train breakdown",
        user=normal_user,
        mode=train_mode,
    )
    db.session.add_all([trip1, trip2])
    db.session.commit()

    login_user(client)
    response = client.get("/trip-history?date=2026-03-30")

    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Birmingham" in html
    assert "London" not in html
    assert "walk breakdown" in html
    assert "train breakdown" not in html


# T-JE-09: Trip history only shows the logged-in user's trips
def test_trip_history_only_shows_logged_in_users_trips_for_my_feature(
    client, app_context, normal_user, second_user, walking_mode, train_mode
):
    trip1 = Trip(
        distance_km=2.0,
        carbon_emission=0.0,
        score_earned=8.0,
        location="Birmingham",
        location_normalized="birmingham",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="matt trip",
        user=normal_user,
        mode=walking_mode,
    )
    trip2 = Trip(
        distance_km=10.0,
        carbon_emission=0.4,
        score_earned=6.0,
        location="Leeds",
        location_normalized="leeds",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="alice trip",
        user=second_user,
        mode=train_mode,
    )
    db.session.add_all([trip1, trip2])
    db.session.commit()

    login_user(client)
    response = client.get("/trip-history")

    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Birmingham" in html
    assert "matt trip" in html
    assert "Leeds" not in html
    assert "alice trip" not in html

