"""
Navigation feature tests — Sam McQ
T-SM-01: HERE API returns a valid route distance
T-SM-02: Navigation rejects empty or invalid location input
T-SM-03: System handles HERE API failure without crashing
"""

import json
from unittest.mock import patch, MagicMock
from tests.conftest import login_user


# ── Shared mock HERE API response ────────────────────────────────────────────

def make_here_response(length_m=7500, duration_s=900):
    """
    Returns a mock requests.Response that mimics a successful HERE Routing API reply.
    length_m  — route length in metres (default 7.5 km)
    duration_s — journey duration in seconds (default 15 min)
    """
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "routes": [{
            "sections": [{
                "summary": {
                    "length":   length_m,
                    "duration": duration_s,
                },
                "polyline": "BFoz5xJ67i1B1B7PzIhaUxL7YUx",
            }]
        }]
    }
    return mock_resp


# - T-SM-01
# HERE API returns a valid route distance between two locations

def test_here_api_returns_valid_route_distance(client, app_context, normal_user):
    """
    Given a logged-in user and valid start/end coordinates,
    When the navigate/route endpoint is called with a mocked HERE response of 7500m,
    Then the response contains distance_km = 7.5 for the car mode
    """
    login_user(client)

    with patch("app.routes.http_requests.get", return_value=make_here_response(length_m=7500)):
        response = client.post(
            "/navigate/route",
            data=json.dumps({
                "origin":      "51.5074,-0.1278",   # London
                "destination": "51.4700,-0.4543",   # Heathrow
            }),
            content_type="application/json",
        )

    assert response.status_code == 200

    data = response.get_json()

    # Car mode should be available
    assert data["car"]["available"] is True

    # Distance should be 7.5 km (7500m / 1000, rounded to 1dp)
    assert data["car"]["distance_km"] == 7.5

    # Duration should be present and non-empty
    assert data["car"]["duration"] != ""

    # CO2 should be a non-negative number
    assert data["car"]["co2_kg"] >= 0


# ─ T-SM-02
# Navigation rejects empty or invalid location input

def test_navigation_rejects_empty_origin(client, app_context, normal_user):
    """
    Given a logged-in user,
    When navigate/route is called with an empty origin,
    Then a 400 response is returned with a validation error message.
    No trip is logged and no score is calculated.
    """
    login_user(client)

    response = client.post(
        "/navigate/route",
        data=json.dumps({
            "origin":      "",
            "destination": "51.4700,-0.4543",
        }),
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Origin and destination are required"


def test_navigation_rejects_empty_destination(client, app_context, normal_user):
    """
    Given a logged-in user,
    When navigate/route is called with an empty destination,
    Then a 400 response is returned with a validation error message.
    """
    login_user(client)

    response = client.post(
        "/navigate/route",
        data=json.dumps({
            "origin":      "51.5074,-0.1278",
            "destination": "",
        }),
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Origin and destination are required"


def test_navigation_rejects_both_fields_empty(client, app_context, normal_user):
    """
    Given a logged-in user,
    When navigate/route is called with both origin and destination empty,
    Then a 400 response is returned.
    """
    login_user(client)

    response = client.post(
        "/navigate/route",
        data=json.dumps({"origin": "", "destination": ""}),
        content_type="application/json",
    )

    assert response.status_code == 400


# ─ T-SM-03
# System handles HERE API failure without crashing

def test_here_api_failure_returns_unavailable_modes(client, app_context, normal_user):
    """
    Given a logged-in user and valid coordinates
    When the HERE API is unreachable (raises ConnectionError)
    Then the endpoint returns 200 with all modes marked as unavailable
    """
    import requests

    login_user(client)

    with patch("app.routes.http_requests.get", side_effect=requests.exceptions.ConnectionError):
        response = client.post(
            "/navigate/route",
            data=json.dumps({
                "origin":      "51.5074,-0.1278",
                "destination": "51.4700,-0.4543",
            }),
            content_type="application/json",
        )

    assert response.status_code == 200

    data = response.get_json()

    # All three modes should be present but unavailable
    for mode in ("car", "pedestrian", "publicTransport"):
        assert mode in data
        assert data[mode]["available"] is False


def test_here_api_timeout_handled_gracefully(client, app_context, normal_user):
    """
    Given a logged-in user and valid coordinates,
    When the HERE API times out,
    Then the endpoint returns 200 with all modes marked as unavailable
    """
    import requests

    login_user(client)

    with patch("app.routes.http_requests.get", side_effect=requests.exceptions.Timeout):
        response = client.post(
            "/navigate/route",
            data=json.dumps({
                "origin":      "51.5074,-0.1278",
                "destination": "51.4700,-0.4543",
            }),
            content_type="application/json",
        )

    assert response.status_code == 200

    data = response.get_json()

    for mode in ("car", "pedestrian", "publicTransport"):
        assert data[mode]["available"] is False
