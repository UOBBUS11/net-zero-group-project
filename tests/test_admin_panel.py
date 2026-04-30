import pytest
from tests.conftest import login_admin, login_user
from app.models import TransportMode


# T-AU-1A: Unauthenticated users are redirected from the admin panel
def test_admin_panel_access_denied_unauthenticated(client):
    response = client.get("/admin", follow_redirects=True)
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Admin access only." in html
    assert "Login" in html


# T-AU-2B: Normal logged-in users cannot access the admin panel
def test_admin_panel_access_denied_normal_user(client, normal_user):
    login_user(client, username="matt", password="password123")
    response = client.get("/admin", follow_redirects=True)
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Admin access only." in html
    assert "Login" in html


# T-AU-3C: Authenticated admins can view the admin panel
def test_admin_panel_access_granted(client, admin_user):
    login_admin(client)
    response = client.get("/admin")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Admin Panel: Scoring Rules" in html


# T-AU-4D: Admin can update transport mode scoring rules
def test_admin_panel_update_transport_mode(client, admin_user, walking_mode, app_context):
    login_admin(client)

    new_emission = 0.05
    new_base = 3.0
    new_per_km = 0.20

    response = client.post(
        "/admin",
        data={
            "mode_id": walking_mode.id,
            "emission_factor": new_emission,
            "base_points": new_base,
            "points_per_km": new_per_km,
            "submit": "Update Rule"
        },
        follow_redirects=True
    )
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Updated scoring rule for Walking." in html

    updated_mode = TransportMode.query.filter_by(mode_name="Walking").first()
    assert updated_mode.emission_factor == new_emission
    assert updated_mode.base_points == new_base
    assert updated_mode.points_per_km == new_per_km
